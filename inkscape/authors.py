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
Provide author information from bzr and other sources.
"""

from os.path import isfile, join
from collections import OrderedDict
import datetime

from django.conf import settings

class AuthorRecord(OrderedDict):
    """Record a bazaar or git log in an author centric way"""
    def add_bzr_log(self, log_file):
        if isfile(log_file):
            with open(log_file, 'r') as fhl:
                for block in fhl.read().split('-' * 50):
                    self.add_bzr_block(block)

    def add_git_log(self, log_file):
        if isfile(log_file):
            with open(log_file, 'r') as fhl:
                for block in fhl.read().split('-' * 18):
                    self.add_git_block(block)

    def add_bzr_block(self, blk):
        """Turn a colon seperated name/value pair into a dict"""
        dat = dict(l.strip().split(':', 1) for l in blk.split('\n') if ':' in l)
        if not dat or 'Launchpad' in dat['committer']:
            return
        date = [int(i) for i in dat['timestamp'].strip().split(' ')[1].split('-')]
        if '<' in dat['committer']:
            (name, email) = dat['committer'].strip().strip('>').split('<', 1)
            name = name.strip()
        elif '@' in dat['committer']:
            name = dat['committer'].split('@')[0].strip()
            email = dat['committer'].strip()
        else:
            name = dat['committer'].strip()
            email = None

        author = self.setdefault(name.lower(), {
            'count': 0, 'start': 3000, 'end': 0,
            'emails': set(), 'name': name,
        })
        if email:
            author['emails'].add(email)

        author['count'] += 1
        if date[0] < author['start']:
            author['start'] = date[0]
        if date[0] > author['end']:
            author['end'] = date[0]

    def add_git_block(self, blk):
        """Turn a pretty-printed git log into a dict"""
        dat = dict(l.strip().split(':', 1) for l in blk.split('\n') if ':' in l)

        if not dat or 'Launchpad' in dat['AUTHOR']:
            return

        date = datetime.date.fromtimestamp(float(dat['TIME'])).year
        name = dat['AUTHOR']
        email = dat['EMAIL']

        author = self.setdefault(name.lower(), {
            'count': 0, 'start': 3000, 'end': 0,
            'emails': set(), 'name': name,
        })
        # currently not used for anything, could be used to connect with account at inkscape.org
        if email:
            author['emails'].add(email)

        author['count'] += 1
        if date < author['start']:
            author['start'] = date
        if date > author['end']:
            author['end'] = date


CODERS = AuthorRecord()
TRANSLATORS = AuthorRecord()
DOCUMENTORS = AuthorRecord()

PATH = settings.PROJECT_PATH

CODERS.add_git_log(join(PATH, 'data', 'revision.log'))
DOCUMENTORS.add_git_log(join(PATH, 'data', 'documentation.log'))
TRANSLATORS.add_git_log(join(PATH, 'data', 'translators.log'))

# XXX
# The translators are often obscured in the bzr log, so we want to
# add po file credits too, this is a TODO item to improve credit to
# translators.
