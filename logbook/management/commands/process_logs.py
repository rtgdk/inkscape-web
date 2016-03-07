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
Django command for processing log files.
"""

import os
import sys

from django.core.management.base import NoArgsCommand

from logbook.settings import get_setting
from logbook.parser import parse_logs
from logbook.analysis import process_results

BAR_CACHE = {}
def progress_bar(label, loc, count, done):
    """Creates a progress bar for this process if OUTPUT is true"""
    label += " " * (6 - len(label[:6]))
    if BAR_CACHE.get(label, 0) != int(loc * 200):
        sys.stdout.write(label[:6] + ' ')
        sys.stdout.write('|' + ("=" * int(loc * 50)))
        sys.stdout.write(("-" * (50 - int(loc * 50))) + '| ')
        sys.stdout.write('%d%% (%d/%d)\r' % (int(loc * 100), count, done))
        sys.stdout.flush()
        BAR_CACHE[label] = int(loc * 200)
    if loc == 1.0:
        sys.stderr.write("\n")


class Command(NoArgsCommand):
    """Command"""
    help = "Process yesterday's log files into the database"

    def handle_noargs(self, **options):
        result = parse_logs(
            os.path.join(get_setting('ROOT'), '%(key)s', 'access.log.1'),
            progress=progress_bar,
          )
        process_results(result, progress=progress_bar)

