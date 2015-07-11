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

from django.core.urlresolvers import reverse
from django.views.generic import UpdateView, CreateView
from django.utils.translation import ugettext_lazy as _

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
            for name in ('object', 'parent', 'action', 'view'):
                out[name] = response.context_data.get(name, None)
            if not out.get('action', None) and 'view' in out:
                out['action'] = self._action(out['view'])
            response.context_data['breadcrumbs'] = self._crumbs(**out)
        return response

    def _crumbs(self, object=None, parent=None, action=None, **kwargs):
        yield (reverse('pages-root'), _('Home'))
        target = object if object is not None else parent
        if target is not None:
            for obj in self._ancestors(target):
                if hasattr(obj, 'get_absolute_url'):
                    yield (obj.get_absolute_url(), self._name(obj))
                else:
                    yield (None, self._name(obj))

        if action is not None:
            yield (None, _(action))

    def _action(self, view):
        if isinstance(view, UpdateView):
            return _("Edit")
        elif isinstance(view, CreateView):
            return _("New")
        return None

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

