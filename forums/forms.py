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
from django_comments.forms import CommentForm, ContentType, ErrorDict

from .models import Forum, ForumTopic

class AddCommentForm(CommentForm):
    """This CommentForm replaces the django_comments one, what it provides is
       comment thread locking which is global no matter where the comment is.
    """
    def is_locked(self, **kw):
        """Return true if this configured comment form is locked"""
        pk = kw.get('object_pk', self.initial['object_pk'])
        if isinstance(self.target_object, ForumTopic):
            topics = ForumTopic.objects.filter(pk=pk)
        else:
            ct = ContentType.objects.get_for_model(self.target_object)
            topics = ForumTopic.objects.filter(object_pk=pk, forum__content_type_id=ct.pk)
        return any(topics.values_list('locked', flat=True))

    def clean_object_pk(self):
        """Check to see if this object is locked"""
        if self.is_locked(object_pk=self.cleaned_data["object_pk"]):
            raise ValidationError("This comment thread is locked.")
        return self.cleaned_data['object_pk']

    def security_errors(self):
        """Return just those errors associated with security"""
        errors = ErrorDict()
        for f in ["honeypot", "timestamp", "security_hash", "object_pk"]:
            if f in self.errors:
                errors[f] = self.errors[f]
        return errors



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
        

