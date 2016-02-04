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
Django command for clearing fastly caches.
"""

import os
import sys
import time
import fastly

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.templatetags.static import static

def touch(fname, times=None):
    """Unix like touching of files"""
    with open(fname, 'a'):
        os.utime(fname, times)

class Command(NoArgsCommand):
    """Clear fastly cache based on last clear and modified times"""
    help = "Cleans the static files from a fastly cache"

    def __init__(self, *args, **kwargs):
        self.api = None
        super(Command, self).__init__(*args, **kwargs)

    def handle_noargs(self, **options):
        key = settings.FASTLY_CACHE_API_KEY
        if key:
            self.api = fastly.API()
            self.api.authenticate_by_key(key)
            self.purge_all()

    def purge_all(self, old=False):
        """
          Purge all new static files from cache,

          purge old ones too if old=True (all static files)
        """
        root = settings.STATIC_ROOT

        if not os.path.isdir(root):
            return sys.stderr.write("\nStatic directory doesn't exist or is "
                "empty. Have you run collectstatic yet?\n\n")

        elif 'fastly.net' not in settings.STATIC_URL:
            return sys.stderr.write("Fastly not being used for this website."
                "(set STATIC_URL)\n")

        last_clear = 0
        last_file = os.path.join(root, '.fastly_cleared')
        if os.path.isfile(last_file):
            last_clear = os.path.getmtime(last_file)
            print "Last cache clear: %s" % time.ctime(last_clear)
        else:
            print "Never cleared before (first run)"

        count = 0
        cleared = 0

        for name, _, files in os.walk(root, topdown=False):
            for fname in files:
                path = os.path.join(name, fname)
                if path == last_file:
                    continue
                count += 1

                if old or os.path.getmtime(path) > last_clear:
                    cleared += 1
                    self.purge(path.replace(root, '').lstrip('/'))

        print "\n  * %d of %d static files cleared\n\n" % (cleared, count)
        if not count:
            print "There weren't any static files, run collectstatic."

        if cleared:
            touch(last_file)

    def purge(self, path):
        """Purge any static file from the fastly cache"""
        # We don't want to just use get static url, because that just points
        # back to fastly cache which is not what we need for this api
        url = static(path)
        (domain, location) = url.split('://', 1)[-1].split('/', 1)
        self.api.purge_url(domain, '/' + location)

