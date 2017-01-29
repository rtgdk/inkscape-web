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
Some generic utilities for improving caching and other core features
"""

from django.core.exceptions import FieldDoesNotExist

from django.db.models.lookups import Exact
from django.db.models.expressions import Col

from django.template.context import Context

def IterObject(t=list):
    """Create an object from a generator function, default is list"""
    def _outer(f):
        def _inner(*args, **kwargs):
            return t(f(*args, **kwargs))
        return _inner
    return _outer


def context_items(context):
    """Unpack a django context, equiv of dict.items()"""
    if not isinstance(context, Context):
        context = [context]
    for d in context:
        for (key, value) in d.items():
            yield (key, value)

class QuerySetWrapper(object):
    """
    When wrappd around a django QuerySet object using the clone method
    this class will provide you a callback mechanism so every consumed
    iterator will call the method given as it's consumed.

    This is helpful because a queryset might contain thousands of possible
    objects but the template may only consume twenty on a page. We can now
    get a callback for each of those twenty consumed objects, no matter
    what page is being requested.

    Use:

    def func(obj, **kwargs):
        # perhaps action here

    qs._clone(klass=QuerySetWrapper, method=func, [kwargs={...}])

    """
    def iterator(self):
        for obj in super(QuerySetWrapper, self).iterator():
            if self.method is not None:
                self.method(obj, **getattr(self, 'kwargs', {}))
            yield obj

    def _clone(self, klass=None, setup=False, **kwargs):
        c = super(QuerySetWrapper, self)._clone(klass, **kwargs)
        c.method = self.method
        c.kwargs = getattr(self, 'kwargs', {})
        return c

    def get_basic_filter(self):
        """Generator of field/values for all exact matchs in this qs"""
        for child in self.query.where.children:
            if isinstance(child, Exact) and \
               isinstance(child.lhs, Col) and not isinstance(child.rhs, Col):
                ret = self._basic_filter(child.lhs.target, child.rhs, child.lhs.alias)
                if ret:
                    yield ret

    def _basic_filter(self, target, value, alias=None):
        name = None
        if self.model == target.model:
            name = target.name
        elif target.model._meta._forward_fields_map[target.name].unique:
            # For fields like slug, id and other unqiue fields
            name = alias.split('_', 1)[-1]
            try:
                field = self.model._meta.get_field_by_name(name)
            except FieldDoesNotExist:
                return

            qs = target.model.objects.filter(**{target.name: value})
            if qs.count() == 0:
                return

            value = qs.values_list('pk', flat=True)[0]

        if name:
            return (name, value)


class BaseMiddleware(object):
    """
    When used by a middleware class, provides a predictable get()
    function which will provide the first available variable from
    first the context_data, then the view, then the middleware.
    """
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

