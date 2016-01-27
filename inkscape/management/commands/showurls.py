#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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
Shows all the available urls for a django website, useful for debugging.
"""

import inkscape.urls

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = '<start_url>'
    help = 'Shows all urls begining with the start_url'

    def handle(self, *args, **options):
        self.start_url = None
        if len(args) > 0:
            self.start_url = args[0]
        self.show_urls(inkscape.urls.urlpatterns)

    def urls_name(self, uc):
        if isinstance(uc, list) and uc:
            return self.urls_name(uc[0])
        elif hasattr(uc, '__file__'):
            return uc.__file__.split('../')[-1].split('site-packages/')[-1][:-1]
        return None

    def show_urls(self, urllist, depth=0):
        d = "  " * depth
        for entry in urllist:
            p = entry.regex.pattern
            if hasattr(entry, 'url_patterns'):
                name = None
                if hasattr(entry, '_urlconf_module'):
                    name = self.urls_name(entry._urlconf_module)
                self.show_urls(entry.url_patterns, depth + 1)
                if name:
                    self.stdout.write("%s%s > %s" % ( d, p, name ))
            else:
                name = entry.__dict__.get('name', '[Undefined]') or '[Unnammed]'
                self.stdout.write("%s'%s' | %s" % ( d, name, p))




