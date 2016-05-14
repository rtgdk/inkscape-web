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
I can't believe I had to re-write this after copying over it.
"""

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from django.forms import *
from django_comments.forms import CommentForm

from .models import Forum, ForumTopic

class NewTopicForm(CommentForm):
    subject = CharField()
    name = None
    email = None

    def __init__(self, user, ip_address, *args, **kwargs):
        self.user = user
        self.ip = ip_address
        super(NewTopicForm, self).__init__(*args, **kwargs)

    def save(self, **kw):
        subject = self.cleaned_data['subject']
        self.target_object = self.target_object.topics.create(
                subject=subject, last_posted=now())
        
        self.cleaned_data['name'] = self.user.username
        self.cleaned_data['email'] = self.user.email

        comment = self.get_comment_object()
        comment.user = self.user
        comment.ip_address = self.ip
        comment.save()

        return self.target_object
        

