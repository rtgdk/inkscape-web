
from django.db.models import *

from django.utils.translation import ugettext_lazy as _
from alerts.models import BaseAlert, register_alert, CATEGORY_SYSTEM_TO_USER

from cms.models import Page
import cms.signals as cms_signals

class PagePublishedAlert(BaseAlert):
    """Add an alert when a page is edited for anyone subscribed"""

    name     = _("Page Published Alerts")
    desc     = _("An alert is sent each time a page is published (not edited).")
    category = CATEGORY_SYSTEM_TO_USER
    signal   = cms_signals.post_publish
    sender   = Page

    subject  = _("Page Published: ") + "{{ instance }}"
    email_subject = _("Page Published: ") + "{{ instance }}"

    def call(self, sender, **kwargs):
        from reversion import get_for_object
        objs = get_for_object(kwargs['instance'])
        if objs:
            kwargs['revision'] = objs[0].revision
            return super(PagePublishedAlert, self).call(sender, **kwargs)

register_alert('cms_page_published', PagePublishedAlert)

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

