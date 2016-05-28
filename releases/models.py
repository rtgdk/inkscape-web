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
from collections import defaultdict

from django.db.models import *
from django.conf import settings

from django.utils.translation import get_language, ugettext_lazy as _
from django.utils.timezone import now
from django.utils.text import slugify

from django.contrib.contenttypes.models import ContentType

from django.core.cache import caches
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator

from pile.fields import ResizedImageField

null = dict(null=True, blank=True)
DEFAULT_LANG = settings.LANGUAGE_CODE.split('-')[0]
OTHER_LANGS = list(i for i in settings.LANGUAGES if i[0].split('-')[0] != DEFAULT_LANG)
User = settings.AUTH_USER_MODEL

CACHE = caches['default']

def upload_to(name, w=960, h=300):
    return dict(null=True, blank=True, upload_to='release/'+name,\
                  max_height=h, max_width=w)


class ReleaseQuerySet(QuerySet):
    def __init__(self, *args, **kw):
        super(ReleaseQuerySet, self).__init__(*args, **kw)
        self.query.select_related = True

    def for_parent(self, parent):
        pk = parent.parent_id if parent.parent_id else parent.pk
        return self.filter(Q(parent__isnull=True) | Q(parent_id=pk))


class Release(Model):
    """A release of inkscape"""
    parent = ForeignKey('self', related_name='children', **null)
    version = CharField(_('Version'), max_length=8, db_index=True, unique=True)
    codename = CharField(_('Codename'), max_length=32, db_index=True, **null)

    release_notes = TextField(_('Release notes'), **null)
    release_date = DateField(_('Release date'), db_index=True, **null)

    edited = DateTimeField(_('Last edited'), auto_now=True)
    created = DateTimeField(_('Date created'), auto_now_add=True,
                                                     db_index=True)
    background = ResizedImageField(**upload_to('background', 960, 360))

    manager = ForeignKey(User, related_name='releases',
        help_text=_("Looks after the release schedule and release meetings."), **null)
    reviewer = ForeignKey(User, related_name='rev_releases',
        help_text=_("Reviewers help to make sure the release is working."), **null)
    bug_manager = ForeignKey(User, related_name='bug_releases',
        help_text=_("Manages critical bugs and decides what needs fixing."), **null)
    translation_manager = ForeignKey(User, related_name='tr_releases',
        help_text=_("Translation managers look after all translations for the release."),
        **null)

    objects = ReleaseQuerySet.as_manager()

    class Meta:
        ordering = '-release_date',
        get_latest_by = 'release_date'

    def __str__(self):
        if not self.codename:
            return "Inkscape %s" % self.version
        return "Inkscape %s (%s)" % (self.version, self.codename)

    def get_absolute_url(self):
        return reverse('releases:release', kwargs={'version': self.version})

    def is_prerelease(self):
        """Returns True if this child release happened before parent release"""
        (par, dat) = (self.parent, self.release_date)
        return par and dat and (not par.release_date or par.release_date > dat)

    def get_notes(self):
        """Returns a translated release notes"""
        lang = get_language()
        if not lang or lang == DEFAULT_LANG:
            return self.release_notes
        try:
            return self.translations.get(language=lang).translated_notes
        except ReleaseTranslation.DoesNotExist:
            return self.release_notes

    @property
    def revisions(self):
        return Release.objects.filter(Q(parent_id=self.pk) | Q(id=self.pk))

    @property
    def latest(self):
        return self.revisions.order_by('-release_date')[0]

    def responsible_people(self):
        """Quick list of all responsible people with labels"""
        for key in ('manager', 'reviewer', 'translation_manager', 'bug_manager'):
            yield (getattr(Release, key).field.verbose_name,
                   getattr(Release, key).field.help_text,
                   getattr(self, key))


class ReleaseTranslation(Model):
    """A translation of a Release"""
    release = ForeignKey(Release, related_name='translations')
    language = CharField(_("Language"), max_length=8, choices=OTHER_LANGS, db_index=True,
                         help_text=_("Which language is this translated into."))
    translated_notes = TextField(_('Release notes'))


class Platform(Model):
    """A list of all platforms we release to"""
    name       = CharField(_('Name'), max_length=64)
    desc       = CharField(_('Description'), max_length=255)
    parent     = ForeignKey('self', related_name='children', verbose_name=_("Parent Platform"), **null)
    manager    = ForeignKey(User, verbose_name=_("Platform Manager"), **null) 
    codename   = CharField(max_length=255, **null)
    order      = PositiveIntegerField(default=0)

    match_family = CharField(max_length=32, db_index=True,
            help_text=_('User agent os match, whole string.'), **null)
    match_version = CharField(max_length=32, db_index=True,
            help_text=_('User agent os version partial match, e.g. |10|11| will match both version 10 and version 11, must have pipes at start and end of string.'), **null)
    match_bits = PositiveIntegerField(db_index=True, choices=((32, '32bit'), (64, '64bit')), **null)

    icon       = ResizedImageField(**upload_to('icons', 32, 32))
    image      = ResizedImageField(**upload_to('icons', 256, 256))

    uuid       = lambda self: slugify(self.name)
    tab_name   = lambda self: self.name
    tab_text   = lambda self: self.desc
    tab_cat    = lambda self: {'icon': self.icon}
    root       = lambda self: self.ancestors()[-1]
    depth      = lambda self: len(self.ancestors) - 1

    class Meta:
        ordering = '-order', 'codename'

    def save(self, **kwargs):
        codename = "/".join([slugify(anc.name) for anc in self.ancestors()][::-1])
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
        return self.codename.replace('/', ' : ').replace('_', ' ').title()


class PlatformQuerySet(QuerySet):
    def __init__(self, *args, **kw):
        super(PlatformQuerySet, self).__init__(*args, **kw)
        self.query.select_related = True

    def for_os(self, family, version, bits):
        """Returns all ReleasePlatforms that match the given user_agent os"""
        qs = self.filter(platform__match_family=family)
        # Set version to a single point precision
        version = '|' + str(version) + '|'
        qs = qs.filter(Q(platform__match_version__contains=version) |
                       Q(platform__match_version__isnull=True) |
                       Q(platform__match_version=''))
        qs = qs.filter(Q(platform__match_bits=bits) |
                       Q(platform__match_bits__isnull=True))
        return qs.order_by('platform__match_family', 'platform__match_version')

    def for_level(self, parent=''):
        """Returns a list of Platforms which are in this release"""
        # This conditional is required because codename at the zeroth
        # level is '' but the first level is 'windows', they have the
        # same number of forward slashes.
        level = parent.count('/') + 2 if parent else 1

        items = defaultdict(list)
        for release in self:
            codename = release.platform.codename
            if codename.startswith(parent):
                items['/'.join(codename.rsplit('/')[:level])].append(release)

        # Get all platforms at this level
        platforms = list(Platform.objects.filter(codename__in=items.keys()))

        # Add link to a release (download) if it's the only one so downloads
        # can be direct for users.
        for platform in platforms:
            if len(items[platform.codename]) == 1:
                platform.release = items[platform.codename][0]
        return platforms


class ReleasePlatform(Model):
    release = ForeignKey(Release, verbose_name=_("Release"), related_name='platforms')
    platform = ForeignKey(Platform, verbose_name=_("Release Platform"), related_name='releases')
    download = URLField(_('Download Link'), **null)
    howto = URLField(_('Instructions Link'), **null)
    info = TextField(_('Release Platform Information'), **null)

    created = DateTimeField(_("Date created"), auto_now_add=True, db_index=True)

    objects = PlatformQuerySet.as_manager()

    def __str__(self):
        return "%s - %s" % (self.release, self.platform)

    def get_absolute_url(self):
        return reverse('releases:platform', kwargs={
            'version': self.release.version,
            'platform': self.platform.codename,
        })

    def get_download_url(self):
        """Returns a download link with a thank you"""
        return reverse('releases:download', kwargs={
            'version': self.release.version,
            'platform': self.platform.codename,
        })

    @property
    def parent(self):
        if self.platform.parent_id:
            return ReleasePlatform(release=self.release, platform=self.platform.parent)
        return self.release

    def breadcrumb_name(self):
        return self.platform.name

