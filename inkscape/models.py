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

from django.db.models import *

from django.utils.translation import ugettext_lazy as _
#from alerts.models import BaseAlert, register_alert, CATEGORY_SYSTEM_TO_USER

from cms.models import Page
import cms.signals as cms_signals

#class PagePublishedAlert(BaseAlert):
#    """Add an alert when a page is edited for anyone subscribed"""
#    name     = _("Page Published Alerts")
#    desc     = _("An alert is sent each time a page is published (not edited).")
#    category = CATEGORY_SYSTEM_TO_USER
#    signal   = cms_signals.post_publish
#    sender   = Page
#
#    subject  = _("Page Published: ") + "{{ instance }}"
#    email_subject = _("Page Published: ") + "{{ instance }}"
#
#    def call(self, sender, **kwargs):
#        from reversion import get_for_object
#        objs = get_for_object(kwargs['instance'])
#        if objs:
#            kwargs['revision'] = objs[0].revision
#            return super(PagePublishedAlert, self).call(sender, **kwargs)

class ErrorLog(Model):
    uri    = CharField(max_length=255, db_index=True)
    status = IntegerField(db_index=True)
    count  = IntegerField(default=0)
    added  = DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return "%s (%d)" % (self.uri, self.status)

    def add(self):
        self.count += 1
        self.save()

