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
    version       = CharField(_('Version'), max_length=8, unique=True)
    codename      = CharField(_('Codename'), max_length=32, **null)

    release_notes = TextField(_('Release notes'), **null)
    release_date  = DateField(_('Release date'), **null)

    edited        = DateTimeField(_('Last edited'), auto_now=True)
    created       = DateTimeField(_('Date created'), auto_now_add=True,
                                                     db_index=True)
    background    = ResizedImageField(**upload_to('background', 960, 300))

    manager       = ForeignKey(User, related_name='manages_releases',
                                    verbose_name=_("Release Manager"), **null)
    reviewer      = ForeignKey(User, related_name='reviews_releases',
                                    verbose_name=_("Release Reviewer"), **null)

    class Meta:
        ordering = '-release_date',
        get_latest_by = 'release_date'

    def __str__(self):
        if not self.codename:
            return "Inkscape %s" % self.version
        return "Inkscape %s (%s)" % (self.version, self.codename)

    def get_absolute_url(self):
        return reverse('release', kwargs={'version': self.version})

    def all_platforms(self):
        result = []
        for release in self.platforms.all():
            result += release.platform.ancestors()
        return list(set(result))

    @property
    def tabs(self):
        platforms = self.all_platforms()
        roots = []
        for platform in platforms:
            if not platform.parent:
                yield platform
            children = platform.children.all()
            releases = list(platform.releases.filter(release=self))
            if len(releases) > 0:
                platform.release = releases[0]
            platform.filtered = [child
                for child in platforms
                    if child in children]


class Platform(Model):
    """A list of all platforms we release to"""
    name       = CharField(_('Name'), max_length=64)
    desc       = CharField(_('Description'), max_length=255)
    parent     = ForeignKey( 'self', related_name='children', verbose_name=_("Parent Platform"), **null)
    manager    = ForeignKey( User, verbose_name=_("Platform Manager"), **null) 
    codename   = CharField(max_length=255, **null)

    icon       = ResizedImageField(**upload_to('icons', 32, 32))
    image      = ResizedImageField(**upload_to('icons', 256, 256))

    uuid       = lambda self: slugify(self.name)
    tab_name   = lambda self: self.name
    tab_text   = lambda self: self.desc
    tab_cat    = lambda self: {'icon': self.icon}
    root       = lambda self: self.ancestors()[-1]
    depth      = lambda self: len(self.ancestors) - 1

    class Meta:
        ordering = 'codename',

    def save(self, **kwargs):
        codename = str(self)
        if self.codename != codename:
            self.codename = codename
            if self.pk:
                for child in self.children.all():
                    child.save()
        return super(Platform, self).save(**kwargs)

    def get_manager(self):
        if self.manager:
            return self.manager
        if self.parent:
            return self.parent.get_manager()
        return None

    def ancestors(self, _to=None):
        _to = _to or [self]
        if self.parent and self.parent not in _to:
            # Prevent infinite loops getting parents
            _to.append(self.parent)
            self.parent.ancestors(_to)
        return _to
      
    def descendants(self, _from=None):
        _from = _from or []
        for child in self.children.all():
            if child in _from:
                # Prevent infinite loops getting children
                continue
            _from.append(child)
            child.descendants(_from)
        return _from

    def __str__(self):
        return (" : ").join([anc.name for anc in self.ancestors()][::-1])


class ReleasePlatform(Model):
    release    = ForeignKey(Release, verbose_name=_("Release"), related_name='platforms')
    platform   = ForeignKey(Platform, verbose_name=_("Release Platform"), related_name='releases')
    download   = URLField(_('Download Link'), **null)
    more_info  = URLField(_('More Info Link'), **null)
    howto      = URLField(_('Instructions Link'), **null)

    created    = DateTimeField(_("Date created"), auto_now_add=True, db_index=True)

    def __str__(self):
        return "%s - %s" % (self.release, self.platform)

