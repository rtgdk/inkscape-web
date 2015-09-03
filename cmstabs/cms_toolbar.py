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

from django.utils.translation import ugettext_lazy as _

from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.toolbar.items import TemplateItem, ButtonList

@toolbar_pool.register
class LiveToolbar(CMSToolbar):
    """Show a NOT LIVE! warning to users when on localhost or staging"""
    def populate(self):
        from django.conf import settings
        if settings.DEBUG:
            # A full menu is not possible with our extra class for flashing red thing.
            #menu = self.toolbar.get_or_create_menu('live', _('NOT LIVE!'), position=0)
            url = 'https://inkscape.org%s' % self.request.path
            self.toolbar.add_link_item(_('NOT LIVE!'), url=url, extra_classes=['debugwarn'], position=0)
            # XXX Add a "Time until next refresh" option here.



@toolbar_pool.register
class LicenseAgreement(CMSToolbar):
    """Show a licensing agreement box for the user to make sure they know."""
    def post_template_populate(self):
        if not self.request.user.has_perm('person.website_cla_agreed'):
            self.remove_all_buttons()
            self.add_agreement_popup()

    def remove_all_buttons(self):
        for item in self.toolbar.right_items +\
                    self.toolbar.items +\
                    self.toolbar.left_items:
            self.toolbar.remove_item(item)

    def add_agreement_popup(self):
        template = 'cms/toolbar/items/license.html'
        context = {'request': self.request}
        item = TemplateItem(template, context, self.toolbar.RIGHT)
        self.toolbar.add_item(item)


