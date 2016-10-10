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
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar

@toolbar_pool.register
class SubscribeToolbar(CMSToolbar):
    """Displace a Subscribe to this page link."""
    def populate(self):
        from alerts.models import AlertType
        menu = self.toolbar.get_or_create_menu('subscribe', _('Alerts'))
        alert = AlertType.objects.get(slug='cmsdiff.page_published_alert')
        subs = self.request.user.alert_subscriptions.filter(alert=alert)
        page = self.request.current_page._wrapped
        if not subs.is_subscribed():
            if page and subs.is_subscribed(page, True):
                menu.add_link_item(_('Unsubscribe from this page'), url=alert.unsubscribe_url(page))
            elif page:
                menu.add_link_item(_('Subscribe to this page'), url=alert.subscribe_url(page))
            menu.add_link_item(_('Subscribe to all pages'), url=alert.subscribe_url())
        else:
            menu.add_link_item(_('Unsubscribe from all pages'), url=alert.unsubscribe_url())

@toolbar_pool.register
class RemoveUndoAndHistory(CMSToolbar):
    """
    Temporary fix to make it impossible for non-admin staff to use 
    the buggy Undo and History functionality (revert to live seems to work okay)
    """

    def post_template_populate(self):
        
        if not self.request.user.is_superuser:
            from cms.toolbar.items import AjaxItem, ModalItem
            
            current_history_menu = self.toolbar.get_menu('history')
        
            if current_history_menu != None:
                for entry in current_history_menu.find_items(AjaxItem):
                    if entry.item.name in ['Undo', 'Redo']:
                        current_history_menu.remove_item(entry.item)
                for entry in current_history_menu.find_items(ModalItem):
                    if entry.item.name == 'View history...':
                        current_history_menu.remove_item(entry.item)
        return