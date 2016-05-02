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

from django.conf import settings

class AuthorRecord(OrderedDict):
    """Record a bazaar log in an author centric way"""
    def add_bzr_log(self, log_file):
        if isfile(log_file):
            with open(log_file, 'r') as fhl:
                for block in fhl.read().split('-' * 50):
                    self.add_bzr_block(block)

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

CODERS = AuthorRecord()
TRANSLATORS = AuthorRecord()
DOCUMENTORS = AuthorRecord()

PATH = settings.PROJECT_PATH
CODERS.add_bzr_log(join(PATH, 'data', 'revision.log'))
TRANSLATORS.add_bzr_log(join(PATH, 'data', 'translators.log'))
DOCUMENTORS.add_bzr_log(join(PATH, 'data', 'documentation.log'))

# XXX
# The translators are often obscured in the bzr log, so we want to
# add po file credits too, this is a TODO item to improve credit to
# translators.

