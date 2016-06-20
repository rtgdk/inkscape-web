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

from inspect import isclass

from django.core.cache import caches
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals, Model, QuerySet
from django.utils.cache import get_cache_key
from django.views.generic import UpdateView, CreateView, ListView

import logging

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
        if isinstance(obj, Model):
            cls.cache.delete_many(list(
                cls.get_caches(obj) & cls.get_caches(type(obj))
            ))

    @classmethod
    def invalidate_all(cls):
        """Invalidate the ENTIRE cache (normally used for debugging)"""
        cls.cache.clear()

    @classmethod
    def get_caches(cls, datum):
        key = cls.get_key(datum)
        return cls.cache.get(key) or set() if key else set()

    @classmethod
    def get_key(cls, datum):
        """Returns a unique key for this object"""
        # Should be replaced with a django-way of generating the key
        if isinstance(datum, Model):
            return "meta:%s-%s" % (type(datum).__name__, str(datum.pk))
        elif isclass(datum) and issubclass(datum, Model):
            return "meta:%s" % datum.__name__
        elif isinstance(datum, (list, tuple)):
            if len(datum) > 0 and isinstance(datum[0], Model):
                return "meta:%s" % type(datum[0]).__name__
        elif isinstance(datum, QuerySet):
            return "meta:%s" % datum.model.__name__
        return None

    def track_cache(self, datum, cache_key):
        key = self.get_key(datum)
        if key is not None:
            caches = self.cache.get(key)
            if not caches:
                caches = set()
            caches.add(cache_key)
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
            self.track_cache(data.get(key, None), cache_key)
        return response


@receiver(signals.post_delete)
def object_deleted(sender, instance, *args, **kw):
    TrackCacheMiddleware.invalidate(instance)

@receiver(signals.post_save)
def object_saved(sender, instance, *args, **kw):
    """Invalidate page caches for an object if not 'updating_fields'"""
    if kw.get('update_fields'):
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
        obj = self.get(data, 'object')
        page = self.get(data, 'current_page')
        if not obj and page:
            # django-cms pages already have Home
            obj = page
        else:
            yield (reverse('pages-root'), _('Home'))

        parent = self.get(data, 'parent')
        title = self.get(data, 'title')
        target = obj if obj is not None else parent

        for obj in self.get_ancestors(target):
            if isinstance(obj, tuple) and len(obj) == 2:
                yield obj
            elif obj is not None:
                yield self.object_link(obj)

        if title is not None:
            yield (None, title)

    def get_ancestors(self, obj):
        parent = getattr(obj, 'parent', None)
        if parent is not None:
            for ans in self.get_ancestors(parent):
                yield ans
        yield obj

    def object_link(self, obj):
        """Get name from object model"""
        url = None
        if hasattr(obj, 'breadcrumb_name'):
            name = obj.breadcrumb_name()
        elif hasattr(obj, 'name'):
            name = obj.name
        else:
            name = unicode(obj)
        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
        return (url, name)

