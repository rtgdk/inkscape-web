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
All the code for showing the design toolbar in the django_debug_toolbar
"""

from __future__ import absolute_import, unicode_literals

from collections import OrderedDict
from os.path import join, normpath

from django.conf import settings
from django.contrib.staticfiles import finders, storage
from django.contrib.staticfiles.templatetags import staticfiles
from django.core.files.storage import get_storage_class
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import LazyObject
from django.utils.translation import ugettext_lazy as _, ungettext

from debug_toolbar import panels
from debug_toolbar.utils import ThreadCollector

class DesignPanel(panels.Panel):
    """
    A panel to display the found staticfiles.
    """
    name = 'design toolbar'
    nav_title = _('Website Design')
    template = 'debug_design/panel.html'

    @property
    def title(self):
        return _("Website design toolbar")

    @property
    def nav_subtitle(self):
        num = self.change_count
        ret = ungettext("%(num)s changes", "%(num)s changes", num)
        return ret % {'num': num}

    def __init__(self, *args, **kwargs):
        super(DesignPanel, self).__init__(*args, **kwargs)
        self.change_count = 0
        self.custom_count = 0

    def enable_instrumentation(self):
        pass

    def disable_instrumentation(self):
        pass

    def process_request(self, request):
        pass

    def generate_stats(self, request, response):
        pass
        #used_paths = collector.get_collection()
        #self._paths[threading.currentThread()] = used_paths

        #self.record_stats({
        #    'num_found': self.num_found,
        #    'num_used': self.num_used,
        #    'staticfiles': used_paths,
        #    'staticfiles_apps': self.get_staticfiles_apps(),
        #    'staticfiles_dirs': self.get_staticfiles_dirs(),
        #    'staticfiles_finders': self.get_staticfiles_finders(),
        #})

