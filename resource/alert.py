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

from django.db.models import signals
from django.dispatch import Signal

from alerts.base import EditedAlert
from alerts.models import AlertType

from .models import Resource

post_publish = Signal(providing_args=["instance"])

class ResourceAlert(EditedAlert):
    name     = _("New Gallery Resource")
    desc     = _("An alert is sent when the target user submits a resource.")
    category = AlertType.CATEGORY_USER_TO_USER
    sender   = Resource

    subject       = "{% trans 'New submission:' %} {{ instance }}"
    email_subject = "{% trans 'New submission:' %} {{ instance }}"
    object_name   = "{{ object }}'s {% trans 'Gallery Submissions' %}"
    default_email = False
    signal        = post_publish

    # We subscribe to the user of the instance, not the instance.
    target_field = 'user'


