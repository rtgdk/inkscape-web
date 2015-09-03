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
CMS alerts
"""

from django.utils.translation import ugettext_lazy as _

from cms.models import Page
from django.utils.translation import get_language

from alerts.base import BaseAlert
from alerts.models import AlertType
from cmsdiff.signals import post_revision

class PagePublishedAlert(BaseAlert):
    name     = _("Website Page Published")
    desc     = _("A page on the website has been published after editing.")
    category = AlertType.CATEGORY_USER_TO_USER
    sender   = Page

    subject       = "{% trans 'Published:' %} {{ instance }}"
    email_subject = "{% trans 'Published:' %} {{ instance }}"
    object_name   = "{{ instance }}'s {% trans 'Website Page Published' %}"
    default_email = False
    signal        = post_revision

    def call(self, *args, **kwargs):
        kwargs['language'] = get_language()
        super(PagePublishedAlert, self).call(*args, **kwargs)

