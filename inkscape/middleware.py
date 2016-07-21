#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#

import logging
from inspect import isclass

from django.core.cache import caches
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text

from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals, Model, Manager, QuerySet
from django.utils.cache import get_cache_key

import logging

#
# Models which are suppressed do not invalidate their caches when they
# are being updated using 'updated_fields' but will for full saves.
#
SUPPRESSED_MODELS = ['User']
#
# Ignored models never invalidate caches.
#
IGNORED_MODELS = ['Session']

class BaseMiddleware(object):
    def get(self, data, key, default=None, then=None):
        """Returns a data key from the context_data, the view, a get
        method on the view or a get method on the middleware in that order.
        
        Returns default (None) if all fail."""
        if key in data:
            return data[key]
        view = data.get('view', None)
        if hasattr(view, key):
            return getattr(view, key)
        if hasattr(view, 'get_'+key):
            return getattr(view, 'get_'+key)()
        if hasattr(then, 'get_'+key):
            return getattr(then, 'get_'+key)(data)
        return default


class TrackCacheMiddleware(BaseMiddleware):
    """
    When we have objects using generic class based views, we're going
    to track the objects in use and record the caching ids related to them

    We're not going to deal with HEAD requests right now, because the author
    does not understand what they are for or how they work during the
    FetchCache process.
    """
    cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
    key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
    cache = caches[settings.CACHE_MIDDLEWARE_ALIAS]

    @classmethod
    def invalidate(cls, obj):
        """We invalidate all caches as needed based on the object's identity"""
        #keys = list(cls.get_keys(obj))
        if isinstance(obj, Model):
            caches = list(cls.get_caches(obj) | cls.get_caches(type(obj)))
            #print "Invalidating Keys: %s > %s" % (str(keys), str(caches))
            cls.cache.delete_many(caches)
        elif isclass(obj) and issubclass(obj, Model):
            caches = list(cls.get_caches(obj))
            #print "Invalidating Keys: %s > %s" % (str(keys), str(caches))
            cls.cache.delete_many(caches)
        else:
            logging.warning("!ERR DEL cache, '%s' is not a model." % str(obj))

    @classmethod
    def invalidate_all(cls):
        """Invalidate the ENTIRE cache (normally used for debugging)"""
        cls.cache.clear()

    @classmethod
    def get_caches(cls, obj):
        caches = set()
        for key in cls.get_keys(obj):
            cache = cls.cache.get(key)
            if cache is not None:
                caches |= cache
        return caches

    @classmethod
    def get_keys(cls, obj):
        """Returns a unique key for this object"""
        if isinstance(obj, Model):
            yield "meta:%s-%s" % (type(obj).__name__, str(obj.pk))
        elif isclass(obj) and issubclass(obj, Model):
            yield "meta:%s" % obj.__name__
        elif isinstance(obj, (list, tuple)):
            if len(obj) > 0 and isinstance(obj[0], Model):
                yield "meta:%s" % type(obj[0]).__name__
        elif isinstance(obj, QuerySet):
            yield "meta:%s" % obj.model.__name__

    def track_cache(self, obj, cache_key):
        for key in self.get_keys(obj):
            caches = self.cache.get(key)
            if not caches:
                caches = set()
            caches.add(cache_key)
            #print "TRACKING: %s > %s" % (key, cache_key)
            # Keep a record of urls causing caches for longer
            self.cache.set(key, caches, int(self.cache_timeout * 1.5))

    def process_response(self, request, response):
        """
        We process the response, looking for the cached key
        """
        if not getattr(request, '_cache_update_cache', False) \
              or not request.method in ('GET', 'HEAD') \
              or not hasattr(response, 'context_data'):
            return response

        cache_key = get_cache_key(request, self.key_prefix, 'GET', cache=self.cache)
        if not cache_key:
            return response

        data = response.context_data
        for obj in self.get(data, 'cache_tracks', []):
            self.track_cache(obj, cache_key)

        for key in ('object', 'object_list'):
            target = data.get(key, None)
            if target is not None:
                self.track_cache(target, cache_key)
        return response


@receiver(signals.post_delete)
def object_deleted(sender, instance, *args, **kw):
    TrackCacheMiddleware.invalidate(instance)

@receiver(signals.post_save)
def object_saved(sender, instance, *args, **kw):
    """Invalidate page caches for an object if not 'updating_fields'"""
    model = type(instance).__name__
    if kw.get('update_fields') and model in SUPPRESSED_MODELS:
        return
    if model in IGNORED_MODELS:
        return
    TrackCacheMiddleware.invalidate(instance)

def generate_list(f):
    # Generates a list from a generator
    def _inner(*args, **kw):
        return list(f(*args, **kw))
    return _inner

class AutoBreadcrumbMiddleware(BaseMiddleware):
    """
    This middleware controls and inserts some breadcrumbs
    into most pages. It attempts to navigate object hierachy
    to find the parent 
    """
    keys = ('breadcrumbs', 'title')

    def process_template_response(self, request, response):
        if not hasattr(response, 'context_data'):
            return response
        data = response.context_data
        for key in self.keys:
            response.context_data[key] = self.get(data, key, then=self)
        return response

    def get_title(self, data):
        """If no title specified in context, use last breadcrumb"""
        if data.get('breadcrumbs', False):
            return list(data['breadcrumbs'])[-1][-1]
        return None

    @generate_list
    def get_breadcrumbs(self, data):
        """Return breadcrumbs only called if no breadcrumbs in context"""
        title = self.get(data, 'title')
        parent = self.get(data, 'parent')
        obj = self.get(data, 'object')
        page = self.get(data, 'current_page')
        if not obj and page:
            # django-cms pages already have Home
            obj = page
        else:
            yield (reverse('pages-root'), _('Home'))

        root = self.get(data, 'breadcrumb_root')
        if root:
            if isinstance(root, list):
                for item in root:
                    yield self.object_link(item)
            else:
                yield self.object_link(root)

        lst = self.get(data, 'object_list')
        if isinstance(lst, (Manager, QuerySet)):
            if obj is None:
                obj = lst
            elif parent is None:
                parent = lst

        for obj in self.get_ancestors(obj, parent):
            link = self.object_link(obj)
            if link is not None:
                yield link

        if title is not None:
            yield (None, title)

    def get_ancestors(self, obj, parent=None):
        if hasattr(obj, 'breadcrumb_parent'):
            parent = obj.breadcrumb_parent()
        else:
            parent = getattr(obj, 'parent', parent)

        if parent is not None:
            for ans in self.get_ancestors(parent):
                yield ans
        yield obj

    def object_link(self, obj):
        """Get name from object model"""
        url = None
        if obj is None or (isinstance(obj, tuple) and len(obj) == 2):
            return obj
        if hasattr(obj, 'breadcrumb_name'):
            name = obj.breadcrumb_name()
        elif hasattr(obj, 'name'):
            name = obj.name
        else:
            name = smart_text(obj, errors='ignore')
        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
        if name is not None and name.startswith('['):
            return None
        return (url, name)

