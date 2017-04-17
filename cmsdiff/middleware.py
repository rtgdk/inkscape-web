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
Provide middleware items for django-cms
"""

from django.db.models import QuerySet

from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from cms.utils import get_language_from_request as get_lang
from cms.toolbar.items import Menu
from cms.constants import LEFT


class ObjectToolbarMiddleware(object):
    """Adds an Objects menu item for quick admin access to current context"""
    def admin_link(self, model, method='change', obj=None):
        ct = ContentType.objects.get_for_model(model)
        bits = (ct.app_label, ct.model, method)
        args = (obj.pk,) if obj else ()
        perm = '%s.%s_%s' % (ct.app_label, method, ct.model)
        if self.request.user.has_perm(perm):
            return reverse('admin:%s_%s_%s' % bits, args=args)
        raise NoReverseMatch("No permission")

    def menu_item(self, label, action, then, obj=None, model=None):
        if obj and not model:
            model = type(obj)

        bits = {'otype': model.__name__}
        self.menu.name = self.menu.name % bits
        try:
            url = self.admin_link(model, action, obj=obj)
        except NoReverseMatch:
            return None
        self.items += 1
        return self.menu.add_modal_item(label % bits, url=url, on_close=then)

    def add_object_menu(self, obj):
        if type(obj).__name__ == 'SimpleLazyObject':
            obj = obj._wrapped

        if not obj:
            return

        br = None
        model = type(obj)

        then = getattr(model, 'get_list_url', lambda: False)
        if self.menu_item(_('New %(otype)s'), 'add', then, model=model):
            br = self.menu.add_break()

        if self.language not in ('en', None):
            then = getattr(obj, 'get_absolute_url', lambda: 'REFRESH_PAGE')()
            if self.menu_item(_('Translate %(otype)s'), 'translate', then, obj):
                br = self.menu.add_break()

        then = getattr(obj, 'get_absolute_url', lambda: 'REFRESH_PAGE')()
        ed = self.menu_item(_('Edit %(otype)s'), 'change', then, obj)

        then = getattr(model, 'get_list_url', lambda: '/')
        de = self.menu_item(_('Delete %(otype)s'), 'delete', then, obj)

        if not (ed or de) and br:
            self.menu.remove_item(br)

    def add_list_menu(self, lst):
        model = None

        if isinstance(lst, QuerySet):
            model = lst.model
        elif lst:
            for item in lst:
                model = type(item)
                break
        else:
            return

        if model:
            then = getattr(model, 'get_list_url', lambda: False)
            self.menu_item(_('New %(otype)s'), 'add', then, model=model)

    def process_template_response(self, request, response):
        if request.user.is_authenticated() and request.user.is_staff:
            self.items = 0
            self.request = request
            self.language = get_lang(request)
            self.toolbar = request.toolbar
            self.menu = Menu("%(otype)s", self.toolbar.csrf_token, side=LEFT)

            context = getattr(response, 'context_data', {})
            self.add_object_menu(context.get('object', None))
            self.add_list_menu(context.get('object_list', None))

            if self.items:
                self.toolbar.menus['object-menu'] = self.menu
                self.toolbar.add_item(self.menu, position=None)

        return response

