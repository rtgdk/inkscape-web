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
Takes the sourceforge backups and generates gallery resource objects.

It attempts to match source forge users to local website users.
"""

from django.core.management.base import BaseCommand, CommandError

import os
from datetime import datetime
from cStringIO import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.timezone import now
from django.conf import settings

from resources.models import Category, License, Gallery, Resource
from person.models import User, Group

from feedparser import parse



def get_sig(filename, content):
    buf = StringIO(content.encode('ascii'))
    buf.seek(0, 2)
    return InMemoryUploadedFile(buf, "text", filename, None, buf.tell(), None)

class Command(BaseCommand):
    help = 'Converts any sourceforge backups to Resource'

    def parse_sf_file(self, summary, published_parsed, media_hash, **kwargs):
        if summary.endswith('.asc'):
            return
        target = summary.split('/', 2)[-1]
        (gname, fname) = target.split('/')
        path = os.path.join(self.SF_DIR, 'files', target)
        target = path.replace(settings.MEDIA_ROOT, '').strip('/')
        if not os.path.isfile(path):
            print(" ! %s" % target)
            return
        print(" . %s" % target)
        dt_create = datetime(*list(published_parsed)[:7] + [now().tzinfo])
        (gallery, created) = Gallery.objects.get_or_create(
            user=self.user, name=gname, group=self.group)
        if created:
            print " > New gallery '%s'" % str(gallery)

        hash_type = 'md5'
        sig_file = path + '.asc'
        if os.path.isfile(sig_file):
            hash_type = 'sig'
            with open(sig_file, 'r') as sigh:
                media_hash = sigh.read()
        sig_file = target.split('/')[-1] + '.' + hash_type
        try:
            sig = get_sig(sig_file, media_hash)
        except:
            sig = None
        name = target.split('/')[-1].rsplit('.', 1)[0]\
            .replace('_', ' ').replace('-', ' ')

        vals = {'license': self.gpl, 'mirror': True, 'created': dt_create, 'owner': False,
                'published': True, 'category': self.category, 'thumbnail': self.thumbnail,
                'user': self.user, 'edited': now(), 'signature': sig, 'name': name}
        (item, created) = Resource.objects.get_or_create(
                download=target, defaults=vals)
        gallery.items.add(item)

        if created:
            print " * New Item '%s'" % str(item)
        else:
            print " . Existing resource '%s'" % str(item)
        return item

    def handle(self, *args, **options):
        self.SF_DIR = os.path.join(settings.MEDIA_ROOT, 'sourceforge')
        self.gpl = License.objects.get(code='GPLv2')
        self.user = User.objects.get(pk=2)
        self.group = Group.objects.get(pk=32)
        self.category = Category.objects.get(pk=12)
        self.thumbnail = 'resources/thumb/old_inkscape.png'

        for filename in os.listdir(self.SF_DIR):
            if filename.endswith('.rss'):
                path = os.path.join(self.SF_DIR, filename)
                print "Looking at: %s" % path
                with open(os.path.join(self.SF_DIR, filename), 'r') as fhl:
                    # The md5 hash is hidden behind the algo attribute
                    feed = parse(fhl.read().replace(' algo="md5"', ''))
                for kwargs in feed['entries']:
                    if self.parse_sf_file(**kwargs):
                        pass

