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
"""
Core middleware for the inkscape website.
"""

import logging
from inspect import isclass

from django.core.cache import caches
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_text, smart_unicode

from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals, Model, Manager, QuerySet
from django.utils.cache import get_cache_key

import logging

from .utils import BaseMiddleware, QuerySetWrapper, generate_list, context_items

#
# Models which are suppressed do not invalidate their caches when they
# are being updated using 'updated_fields' but will for full saves.
#
# XXX We might not need this any more if user pages only invalidate themselves
SUPPRESSED_MODELS = ['User']
#
# Ignored models never invalidate caches.
#
IGNORED_MODELS = ['Session']


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
    def invalidate(cls, obj, created=False):
        """We invalidate all caches as needed based on the object's identity,

        obj     - The django db Model object who's related views should be invalidated
        created - Was this object just created (default False for edit and del)

        """
        caches = set()
        if isinstance(obj, Model):
            caches = cls.get_caches(obj, created)
            caches |= cls.get_caches(type(obj))
        elif isclass(obj) and issubclass(obj, Model):
            caches = cls.get_caches(obj)
        else:
            logging.warning("!ERR DEL cache, '%s' is not a model." % str(obj))
        #print "Invalidating Keys: %s > %s" % (str(keys), str(caches))
        cls.cache.delete_many(list(caches))

    @classmethod
    def invalidate_all(cls):
        """Invalidate the ENTIRE cache (normally used for debugging)"""
        cls.cache.clear()

    @classmethod
    def get_caches(cls, obj, created=False):
        caches = set()
        for key in cls.get_keys(obj, created):
            cache = cls.cache.get(key)
            if cache is not None:
                caches |= cache
        return caches

    @classmethod
    def get_create_key(cls, model, fields):
        # Detect related name here XXX
        add = ["%s=%s" % (a, unicode(b)) for (a, b) in fields]
        add = "&".join(add).replace(' ', '_')
        return "cache:create:%s%s%s" % (model.__name__, "?"[:bool(add)], add)

    @classmethod
    def get_keys(cls, obj, created=False):
        """Returns a unique key for this object.

        obj - Model, object, QuerySet, tuple or list targeting objects
        created - is only used with cls.invalidate()
        """
        if hasattr(obj, '_wrapped'):
            # Unpack SimpleLazyObjects
            obj = obj._wrapped

        if isinstance(obj, Model):
            name = type(obj).__name__
            if created:
                yield "cache:create:%s" % name

                # Look up created keys in use and apply fields from this obj
                for keys in cls.track_fields(type(obj)):
                    # We recompile the key we used below when doing the QuerySet
                    fields = [(key, getattr(obj, key)) for key in keys]
                    yield cls.get_create_key(type(obj), fields)
            else:
                yield "cache:%s-%s" % (type(obj).__name__, str(obj.pk))

        elif isclass(obj) and issubclass(obj, Model):
            yield "cache:%s" % obj.__name__

        elif isinstance(obj, QuerySet):
            if not hasattr(obj, 'get_basic_filter'):
                obj = obj._clone(klass=QuerySetWrapper, method=None)

            fields = sorted(obj.get_basic_filter())
            yield cls.get_create_key(obj.model, fields)

            if fields:
                cls.track_fields(obj.model, fields)

        elif isinstance(obj, (list, tuple)):
            # Add each item, up to a maximium of 20, best to use QuerySets
            for child in obj[:20]:
                for key in cls.get_keys(child):
                    yield key

    @classmethod
    def track_fields(cls, model, fields=None):
        """Track which fields have been used in this object's create scheme"""
        key = 'cache:fields:' + model.__name__
        caches = cls.cache.get(key) or set()
        if fields is not None:
            fields = tuple([name for name, value in fields])
            caches.add(fields)
            cls.cache.set(key, caches, int(cls.cache_timeout * 1.5))
        return caches

    @classmethod
    def track_cache(cls, obj, cache_key):
        """Associate this cache_key (url pointer) with this model object"""
        for key in cls.get_keys(obj):
            yield key
            caches = cls.cache.get(key)
            if not caches:
                caches = set()
            caches.add(cache_key)
            # Keep a record of urls causing caches for longer
            cls.cache.set(key, caches, int(cls.cache_timeout * 1.5))

    def process_template_response(self, request, response):
        if not request.method in ('GET', 'HEAD') \
              or not hasattr(response, 'context_data'):
            return response

        response.cache_keys = set()
        response.cache_tracks = []

        # Late templatetag renders might add some cache tracking
        request.cache_tracks = response.cache_tracks

        for key, value in context_items(response.context_data):
            if isinstance(value, Model):
                # Track this one item being used in the context data
                response.cache_tracks.append(key)
            elif isinstance(value, QuerySet):
                # Track any items that are loaded by wrapping the queryset
                # and then making a callback as each object is loaded.
                value = value._clone(klass=QuerySetWrapper, method=response.cache_tracks.append)
                response.cache_tracks.append(key)
                response.context_data[key] = value

        return response

    def process_response(self, request, response):
        """
        We process the response, looking for the cached key (url pointer)

        This cache_key is then saved against each of the associated
        objects that are found in this request.
        
        1. These objects can be the object or object_list context data
           variables found in many class based views in django. 
        2. They can be the 'cache_tracks' array found in the context_data
           or a property (or property method) of the class based view.
        3. An array of tracked_objects can be populated using the inkscape
           templatetag 'track_object' which is placed into templates that
           express an object and thus where that object should be tracked.

        {% load inkscape %}
        {% for obj in object_list %}
          {% track_object obj %}
        {% endfor %}
        """
        tracks = getattr(response, 'cache_tracks', [])
        if not getattr(request, '_cache_update_cache', False):
            return response

        cache_key = get_cache_key(request, self.key_prefix, 'GET', cache=self.cache)
        if cache_key is None:
            return response

        response.cache_key = cache_key

        for key in tracks:
            if isinstance(key, (str, unicode)):
                obj = response.context_data[key]
            else:
                obj = key
                key = type(obj).__name__
            response.cache_keys |= set(self.track_cache(obj, cache_key))
        return response


@receiver(signals.post_delete)
def object_deleted(sender, instance, **kw):
    TrackCacheMiddleware.invalidate(instance)

@receiver(signals.post_save)
def object_saved(sender, instance, created=False, **kw):
    """Invalidate page caches for an object if not 'updating_fields'"""
    model = type(instance).__name__
    if kw.get('update_fields') and model in SUPPRESSED_MODELS:
        return
    if model in IGNORED_MODELS:
        return
    TrackCacheMiddleware.invalidate(instance, created)


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
            try:
                name = smart_unicode(obj, errors='ignore')
            except UnicodeEncodeError:
                name = "Name Error"
        if hasattr(obj, 'get_absolute_url'):
            url = obj.get_absolute_url()
        if name is not None and name.startswith('['):
            return None
        return (url, name)


class CachedRedirects(object):
    """
    The django/cms system requires A LOT of resources (some 30%) to redirect
    users to the right language or page.

    We will do a better job here by caching such redirects based on language.
    """
    def process_request(self, request):
        """Return a redirect right away"""
        pass

    def process_response(self, request, response):
        """Cache a redirect if possible"""
        return response

