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
"""
Resource alerts
"""
from django.utils.translation import ugettext_lazy as _
from django.dispatch import Signal

from alerts.base import EditedAlert, CreatedAlert
from forums.models import Comment

from .models import Resource

post_publish = Signal(providing_args=["instance"])

class ResourceAlert(EditedAlert):
    name     = _("New Gallery Resource")
    desc     = _("An alert is sent when the target user submits a resource.")
    info     = _("When a user submits a gallery resource, you can get a message if you are subscribed to that user.")
    sender   = Resource

    subject       = "{% trans 'New submission:' %} {{ instance }}"
    email_subject = "{% trans 'New submission:' %} {{ instance }}"
    object_name   = "{{ object }}'s {% trans 'Gallery Submissions' %}"
    default_email = False
    signal        = post_publish

    subscribe_all = True
    subscribe_any = True
    subscribe_own = False

    # We subscribe to the user of the instance, not the instance.
    target_field = 'user'


class CommentAlert(CreatedAlert):
    name     = _("Comment on Resource")
    desc     = _("A new comment on one of your resources")
    info     = _("When a user comments on one of your gallery uploads, you will receive this alert message.")
    sender   = Comment

    subject       = "{% trans 'New comment:' %} {{ instance }}"
    email_subject = "{% trans 'New comment:' %} {{ instance }}"
    object_name   = "{% trans 'Comment on Resource' %}"
    default_email = True

    subscribe_all = False
    subscribe_any = True
    subscribe_own = True

    def get_alert_users(self, instance):
        """Returns the user that owns the resource"""
        obj = instance.content_object
        if isinstance(obj, Resource):
            if instance.user_id != obj.user_id:
                return obj.user


