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

from alerts.base import CreatedAlert
from alerts.models import Message

class MessageAlert(CreatedAlert):
    """Shows overloading of alert signal to process replies as read"""
    name     = _('Personal Message')
    desc     = _('Another user has sent you a personal message.')
    info     = _("When another user on the website sends you a message directly, this is called a <strong>Personal Message</strong>. By default these messages are emailed to you.")
    alert_user = 'recipient'
    sender   = Message

    subject       = "{{ instance.subject }}"
    email_subject = "Message from User: {{ instance.subject }}"
    object_name   = "User's personal messages: {{ object }}"

    default_email = True
    default_irc = False

    subscribe_all = False
    subscribe_any = False
    subscribe_own = True

    def call(self, sender, instance, **kwargs):
        """Marks the message we're replying to as viewed"""
        # This can cause an integrity error if called from a loaddata atomic block
        if super(MessageAlert, self).call(sender, instance=instance, **kwargs):
            if instance.reply_to:
                instance.reply_to.alerts.all().view_all()


class TestMessageAlert(MessageAlert):
    """Used in tests to get different results"""
    object_name   = "Each message themselves for testing"
    alert_user = 'sender'
    test_only = True
    related_name = 'test_alerts'


