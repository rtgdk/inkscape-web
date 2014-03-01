#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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
Models for resource system, provides license, categories and resource downloads.
"""

import os

from django.db.models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group

from datetime import datetime

from inkscape.fields import ResizedImageField

null = dict(null=True, blank=True)
def upto(d, c='resources'):
    return dict(null=True, blank=True, upload_to=os.path.join(c, d))

class License(Model):
    name    = CharField(max_length=64)
    code    = CharField(max_length=16)
    link    = URLField(**null)
    banner  = ResizedImageField(_('License Banner'), 80, 15, **upto('banner', 'license'))
    icon    = ResizedImageField(_('License Icon'), 100, 40, **upto('icon', 'license'))

    at  = BooleanField(_('Attribution'), default=True)
    sa  = BooleanField(_('Copyleft (Share Alike)'), default=False)
    nc  = BooleanField(_('Non-Commercial'), default=False)
    nd  = BooleanField(_('Non-Derivitive'), default=False)
    arr = BooleanField(_('All Rights Reserved'), default=False)

    def is_free(self):
        return not self.nc and not self.nd and not arr

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)


class Category(Model):
    name     = CharField(max_length=64)
    desc     = TextField(**null)

    acceptable_licenses = ManyToManyField(License)

    def __unicode__(self):
        return self.name


class Resource(Model):
    user     = ForeignKey(User, related_name='items')
    name     = CharField(max_length=64)
    desc     = TextField(_('Description'))
    category = ForeignKey(Category, related_name='items')
    license  = ForeignKey(License)
    owner    = BooleanField(_('I own this work'), default=True)

    thumb    = ResizedImageField(_('Thumbnail'), 190, 190, **upto('thumb'))
    download = FileField(_('Consumable File'), **upto('file'))
    source   = FileField(_('Source File'), **upto('source'))

    created  = DateTimeField(default=datetime.now)
    edited   = DateTimeField(**null)
    published= BooleanField(default=True)

    link_url     = URLField(**null)
    download_uri = URLField(**null)
    source_uri   = URLField(**null)

    def __unicode__(self):
        return self.name

    def is_visible(self, user_id):
        return user_id == self.user.id or self.published

    def save(self, *args, **kwargs):
        self.edited = datetime.now()
        return Model.save(self, *args, **kwargs)

