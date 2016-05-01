#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
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

from django.core.cache import DEFAULT_CACHE_ALIAS, caches
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.dispatch import receiver
from django.db.models import signals, Model, QuerySet
from django.utils.cache import get_cache_key
from django.views.generic import UpdateView, CreateView, ListView

import logging

class TrackCacheMiddleware(object):
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
    def get_caches(cls, datum):
        key = cls.get_key(datum)
        return cls.cache.get(key) or set() if key else set()

    @classmethod
    def get_key(cls, datum):
        """Returns a unique key for this object"""
        # Should be replaced with a django-way of generating the key
        if isinstance(datum, Model):
            return "meta:%s-%s" % (type(datum).__name__, str(datum.pk))
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

        for key in ('object', 'object_list'):
            self.track_cache(response.context_data.get(key, None), cache_key)
        return response


@receiver(signals.post_delete)
def object_deleted(sender, instance, *args, **kw):
    TrackCacheMiddleware.invalidate(instance)

@receiver(signals.post_save)
def object_saved(sender, instance, *args, **kw):
    TrackCacheMiddleware.invalidate(instance)



class AutoBreadcrumbMiddleware(object):
    """
    This middleware controls and inserts some breadcrumbs
    into most pages. It attempts to navigate object hierachy
    to find the parent 
    """
    def process_template_response(self, request, response):
        if not hasattr(response, 'context_data'):
            return response
        if 'breadcrumbs' not in response.context_data:
            out = {}
            for name in ('object', 'parent', 'action', 'view', 'title'):
                out[name] = response.context_data.get(name, None)
            if not out.get('action', None) and 'view' in out:
                out['action'] = self._action(out['view'], out['title'])
            response.context_data['title'] = out['action']
            response.context_data['breadcrumbs'] = self._crumbs(**out)
        return response

    def _crumbs(self, object=None, parent=None, action=None, **kwargs):
        yield (reverse('pages-root'), _('Home'))
        target = object if object is not None else parent
        if target is not None:
            for obj in self._ancestors(target):
                if isinstance(obj, tuple) and len(obj) == 2:
                    yield obj
                elif hasattr(obj, 'get_absolute_url'):
                    yield (obj.get_absolute_url(), self._name(obj))
                else:
                    yield (None, self._name(obj))

        if action is not None:
            yield (None, _(action))

    def _action(self, view, title=None):
        if title:
            return title
        name = getattr(view, 'action_name', None)
        if name:
            return name
        elif isinstance(view, UpdateView):
            return _("Edit")
        elif isinstance(view, CreateView):
            return _("New")
        elif isinstance(view, ListView):
            return _("List")

    def _ancestors(self, obj):
        if hasattr(obj, 'parent') and obj.parent:
            for parent in self._ancestors(obj.parent):
                yield parent
        yield obj

    def _name(self, obj):
        if hasattr(obj, 'breadcrumb_name'):
            return obj.breadcrumb_name()
        elif hasattr(obj, 'name'):
            return obj.name
        return unicode(obj)

