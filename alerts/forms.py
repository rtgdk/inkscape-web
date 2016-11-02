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
Forms for the alert system 
"""

from django.forms import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Message

class MessageForm(ModelForm):
    reply_to = IntegerField(widget=HiddenInput, required=False)
    recipient = IntegerField(widget=HiddenInput)

    class Meta:
        model = Message
        fields = ('subject','body', 'recipient', 'reply_to')

    def clean_recipient(self):
        pk = self.cleaned_data['recipient']
        return get_user_model().objects.get(pk=pk)

    def clean_reply_to(self):
        pk = self.cleaned_data['reply_to']
        if pk:
            return Message.objects.get(pk=pk)

