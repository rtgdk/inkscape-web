#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import json

from django.db.models import *

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.utils.timezone import now
from django.core.urlresolvers import reverse

import json

from .base import direct_render

null = {'null':True, 'blank':True}

MSG_CAT = (
  ('?', 'Unknown'),
  ('U', 'User to User'),
  ('S', 'System to User'),
  ('A', 'Admin to User'),
  ('P', 'User to Admin'),
  ('T', 'System to Translator'),
)

class AlertType(Model):
    """All Possible messages that users can recieve, acts as a template"""
    name     = CharField(max_length=64)
    desc     = CharField(max_length=255)

    group    = ForeignKey(Group, verbose_name=_("Limit to Group"), **null)

    msg      = CharField(max_length=255)
    slug     = CharField(max_length=32)
    
    category = CharField(max_length=1, choices=MSG_CAT, default='?')
    enabled  = BooleanField(default=False)

    def send_to(self, user, data=None):
        if not self.group or self.group in user.groups:
            um = UserAlert(user=user, message=self)
            um.save(data=data)
            return um
        return None

    def __str__(self):
        return self.name


class UserAlertSetting(Model):
    user    = ForeignKey(User, related_name='alert_settings')
    alert   = ForeignKey(AlertType, related_name='settings')
    hide    = BooleanField(_("Hide Alerts"), default=True)
    email   = BooleanField(_("Send Email Alert"), default=False)
    
    def __str__(self):
        return "User Alert Setting"


class UserAlert(Model):
    """A single altert for a specific user"""
    user    = ForeignKey(User, related_name='alerts')
    alert   = ForeignKey(AlertType, releated_name='sent')

    subject = CharField(max_length=255)

    created = DateTimeField(auto_now=True)
    read    = DateTimeField(**null)

    link    = CharField(max_length=32, **null)
    kwargs  = TextField(**null)

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        if self.link:
            kwargs = kwargs and json.loads(self.kwargs) or None
            return reverse(self.link, kwargs=kwargs)
        return None

    def save(self, **kwargs):
        data = kwargs.pop('data', None)
        if not self.subject:
            self.subject = direct_render(self.alert.subject, data)
        if isinstance(self.kwargs, dict):
            self.kwargs = json.dumps(self.kwargs)
        Model.save(self, **kwargs)


