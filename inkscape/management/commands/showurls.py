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

from django.core.management.base import BaseCommand, CommandError

from inkscape.url_utils import WebsiteUrls

class Command(BaseCommand):
    args = '<start_url>'
    help = 'Shows all urls begining with the start_url'

    def handle(self, *args, **options):
        self.start_url = None
        if len(args) > 0:
            self.start_url = args[0]

        for url in WebsiteUrls():
            self.stdout.write(" " * url.depth + unicode(url))

