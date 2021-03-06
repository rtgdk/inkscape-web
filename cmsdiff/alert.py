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

from cms.signals import post_publish

class PagePublishedAlert(BaseAlert):
    name     = _("Website Page Published")
    desc     = _("A page on the website has been published after editing.")
    info     = _("When a website editor or translator edits one of the content pages, a message is sent to all subscribers. You can be subscribed to one page or all pages on the website.")
    sender   = Page

    subject       = "{% trans 'Published:' %} {{ instance }}"
    email_subject = "{% trans 'Published:' %} {{ instance }}"
    object_name   = "when the '{{ object }}' page is published"
    default_email = False
    signal        = post_publish

    subscribe_all = True
    subscribe_any = True
    subscribe_own = False

    def call(self, *args, **kwargs):
        if 'language' not in kwargs:
            kwargs['language'] = get_language()
        super(PagePublishedAlert, self).call(*args, **kwargs)

