#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Record and control releases.
"""

import os

from django.db.models import *

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.utils.text import slugify

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator

from pile.models import null
from pile.fields import ResizedImageField

def upload_to(name, w=960, h=300):
    return dict(null=True, blank=True, upload_to='release/'+name,\
                  max_height=h, max_width=w)

class Release(Model):
    """A release of inkscape"""
    version       = CharField(max_length=8, unique=True)
    codename      = CharField(max_length=32, **null)

    release_notes = TextField(**null)
    release_date  = DateField(**null)

    created       = DateTimeField(auto_now_add=True, db_index=True)
    edited        = DateTimeField(auto_now=True)

    manager       = ForeignKey(User, related_name='manages_releases', **null)
    reviewer      = ForeignKey(User, related_name='reviews_releases', **null)

    class Meta:
        ordering = '-version',

    def __str__(self):
        if not self.codename:
            return "Inkscape %s" % self.version
        return "Inkscape %s (%s)" % (self.version, self.codename)

    def get_absolute_url(self):
        return reverse('release', kwargs={'version': self.version})

    @property
    def tabs(self):
        return list(set(specific.platform.root() for specific in self.platforms.all()))


class Platform(Model):
    """A list of all platforms we release to"""
    name       = CharField(max_length=64)
    desc       = CharField(max_length=255)
    parent     = ForeignKey('self', **null)
    manager    = ForeignKey(User, **null) 

    icon       = ResizedImageField(_('Icon (32x32)'),         **upload_to('icons', 32, 32))
    image      = ResizedImageField(_('Logo (256x256)'),       **upload_to('icons', 256, 256))

    uuid     = lambda self: slugify(self.name)
    tab_name = lambda self: self.name
    tab_text = lambda self: self.desc
    tab_cat  = lambda self: {'icon': self.icon}
    root     = lambda self: self.parent.root() if self.parent else self

    def __str__(self):
        return self.name


class ReleasePlatform(Model):
    release    = ForeignKey(Release, related_name='platforms')
    platform   = ForeignKey(Platform, related_name='releases')
    download   = URLField(**null)
    more_info  = URLField(**null)
    howto      = URLField(_('Instructions'), **null)

    created    = DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s - %s" % (self.release, self.platform)

