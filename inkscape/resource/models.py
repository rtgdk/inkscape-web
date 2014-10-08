##
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
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from model_utils.managers import InheritanceManager

from inkscape.settings import MAX_PREVIEW_SIZE
from inkscape.fields import ResizedImageField

from .utils import syntaxer, MimeType, upto, cached
from inkscape.settings import DESIGN_URL

null = dict(null=True, blank=True)

DOMAINS = {
  'inkscape.org': 'Inkscape Website',
  'launchpad.net': 'Launchpad',
  'deviantart.com': 'deviantArt',
  'openclipart.org': 'OpenClipart (OCAL)',
}

class VisibleManager(Manager):
    def get_query_set(self):
        return Manager.get_query_set(self).filter(visible=True)

    def get(self, **kwargs):
        return Manager.get_query_set(self).get(**kwargs)

    def full_list(self):
        return Manager.get_query_set(self)

class License(Model):
    name    = CharField(max_length=64)
    code    = CharField(max_length=16)
    link    = URLField(**null)
    banner  = FileField(_('License Banner (svg:80x15)'), **upto('banner', 'license'))
    icon    = FileField(_('License Icon (svg:100x40)'), **upto('icon', 'license'))

    at  = BooleanField(_('Attribution'), default=True)
    sa  = BooleanField(_('Copyleft (Share Alike)'), default=False)
    nc  = BooleanField(_('Non-Commercial'), default=False)
    nd  = BooleanField(_('Non-Derivitive'), default=False)

    visible  = BooleanField(default=True)
    replaced = ForeignKey("License", verbose_name=_('Replaced by'), **null)

    objects  = VisibleManager()

    def is_free(self):
        return not self.nc and not self.nd and not arr

    def is_all_rights(self):
        return self.nc and self.nd and not self.at

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)


class Category(Model):
    name     = CharField(max_length=64)
    desc     = TextField(**null)

    visible  = BooleanField(default=True)
    acceptable_licenses = ManyToManyField(License)

    objects  = VisibleManager()

    def __unicode__(self):
        return self.name

    @property
    def value(self):
        return self.pk

    def get_absolute_url(self):
        return reverse('resource_category', args=[str(self.id)])


class ResourceManager(InheritanceManager):
    def get_query_set(self):
        return InheritanceManager.get_query_set(self).select_subclasses('resourcefile').order_by('-created')

    def for_user(self, user):
        return self.get_query_set().filter(Q(user=user.id) | Q(published=True))

    def downloads(self):
        return self.get_query_set().aggregate(Sum('downed')).values()[0]

    def views(self):
        return self.get_query_set().aggregate(Sum('viewed')).values()[0]

    def new(self):
        return self.get_query_set().filter(category__isnull=True)

    def trash(self):
        return self.get_query_set().filter(gallery__isnull=True).exclude(category=Category.objects.get(pk=1))

    def pastes(self):
        return self.get_query_set().filter(category=Category.objects.get(pk=1))

    def disk_usage(self):
        # This could be done better by storing the file sizes
        return sum(f.download.size for f in self.get_query_set().filter(resourcefile__isnull=False))


class Resource(Model):
    is_file   = False
    user      = ForeignKey(User, related_name='resources')
    name      = CharField(max_length=64)
    desc      = TextField(_('Description'), **null)
    category  = ForeignKey(Category, related_name='items', **null)

    created   = DateTimeField(default=now)
    edited    = DateTimeField(**null)
    published = BooleanField(default=False)

    thumbnail = ResizedImageField(_('Thumbnail'), 190, 190, **upto('thumb'))

    link      = URLField(_('External Link'), **null)
    viewed    = IntegerField(default=0)
    downed    = IntegerField(_('Downloaded'), default=0)

    media_type = CharField(_('File Type'), max_length=64, **null)

    objects   = ResourceManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.edited = now()
        if not self.media_type:
            self.media_type = self.find_media_type()
        return Model.save(self, *args, **kwargs)

    def find_media_type(self):
        # We don't know how to find it for links yet.
        return None

    def get_absolute_url(self):
        if self.category and self.category.id == 1:
            return reverse('pasted_item', args=[str(self.id)])
        return reverse('resource', args=[str(self.id)])

    @property
    def years(self):
        if self.created.year != self.edited.year:
            return "%d-%d" % (self.created.year, self.edited.year)
        return "%d" % self.edited.year

    def is_visible(self, user):
        return user == self.user or self.published

    @property
    def is_new(self):
        return not self.category

    @property
    def next(self):
        """Get the next item in the gallery which needs information"""
        try:
            return self.gallery.items.new().exclude(pk=self.id)[0]
        except IndexError:
            return None

    @property
    def gallery(self):
        try:
            return self.gallery_set.all()[0]
        except IndexError:
            return None

    @cached
    def mime(self):
        """Returns an encapsulated media_type as a MimeType object"""
        return MimeType( self.media_type or 'application/unknown' )

    def link_from(self):
        """Returns the domain name or useful name if known for link"""
        domain = '.'.join(self.link.split("/")[2].split('.')[-2:])
        return DOMAINS.get(domain, domain)

    def icon(self):
        """Returns a 150px icon either from the thumbnail, the image itself or the mimetype"""
        if self.thumbnail:
            return self.thumbnail.url
        return self.mime().icon()

    @property
    def download(self):
        class NotLocalDownload(object):
            def __init__(self, link):
                self.link = link
            def url(self):
                return self.link
            def path(self):
                return '/'.join(self.link.split('/')[3:])
        return NotLocalDownload(self.link)

OWNS = (
  (None, _('No permission')),
  (True, _('I own the work')),
  (False, _('I have permission')),
)

class ResourceFile(Resource):
    """This is a resource with an uploaded file"""
    is_file = True

    download   = FileField(_('Consumable File'), **upto('file', blank=False))

    license    = ForeignKey(License, **null)
    owner      = BooleanField(_('Permission'), choices=OWNS, default=True)

    def save(self, *args, **kwargs):
        Resource.save(self, *args, **kwargs)

        if self.download and not self.thumbnail:
            # We might be able to detect that the download has changed here.
            if self.mime().is_raster():
                self.thumbnail.save(self.download.name, self.download)
            elif self.thumbnail:
                self.thumbnail = None
            Resource.save(self, *args, **kwargs)

    def find_media_type(self):
        """Returns the media type of the downloadable file"""
        return str(MimeType(filename=self.download.path))

    def icon(self):
        if not self.thumbnail and self.mime().is_image() and self.download.size < MAX_PREVIEW_SIZE:
            return self.download.url
        return Resource.icon(self)

    def as_lines(self):
        """Returns the contents as text"""
        return syntaxer(self.as_text(), self.mime())

    def as_text(self):
        if self.mime().is_text():
            with open(self.download.path, 'r') as fhl:
                return fhl.read().decode('utf-8')
        return "Not text!"


class GalleryManager(Manager):
    def for_user(self, user):
        return self.get_query_set().filter(Q(user=user.id) | Q(items__published=True)).distinct()


class Gallery(Model):
    user      = ForeignKey(User, related_name='galleries')
    group     = ForeignKey(Group, related_name='galleries', **null)
    name      = CharField(max_length=64)
    items     = ManyToManyField(Resource, **null)

    objects   = GalleryManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gallery', args=[str(self.id)])

    def is_visible(self, user=None):
        return self.items.for_user(user).count() or self.is_editable(user)

    def is_editable(self, user=None):
        return user and user.id and (
            self.user == user or user.is_superuser \
              or (user.groups.count() and self.group in user.groups.all()))

    def icon(self):
        if self.items.all().count():
            return self.items.all()[0].icon()
        return os.path.join( DESIGN_URL,'images','folder.svg' )

    def __len__(self):
        return self.items.count()


class VoteManager(Manager):
    def likes(self):
        return self.get_query_set().filter(vote=True)

    def dislikes(self):
        return self.get_query_set().filter(vote=False)

    def for_user(self, user):
        return self.get_query_set().filter(Q(voter=user.id))


class Vote(Model):
    """Vote for a resource in some way"""
    resource = ForeignKey(Resource, related_name='votes')
    voter    = ForeignKey(User, related_name='votes')
    vote     = BooleanField(_('Vote'), default=True)

    objects = VoteManager()
    
    def __str__(self):
        return "%s -> %s -> %s " % (str(self.voter), self.votetype, str(self.resource))

    @property
    def votetype(self):
        return self.vote and "Likes" or "Dislikes"


class Quota(Model):
    group    = ForeignKey(Group, related_name='quotas', unique=True, **null)
    size     = IntegerField(_("Quota Size (bytes)"), default=102400)

    def __str__(self):
        return str(self.group)

# I don't like this much
def quota_for_user(user):
    f = Q(group__in=user.groups.all()) | Q(group__isnull=True)
    return Quota.objects.filter(f).aggregate(Max('size'))['size__max'] or 0

User.quota = quota_for_user

# ------------- CMS ------------ #

from cms.models import CMSPlugin
from inkscape.inline_templates.models import InlineTemplate

class GalleryPlugin(CMSPlugin):
    limit    = PositiveIntegerField(_('Number of items'))
    source   = ForeignKey(Gallery)
    template = ForeignKey(InlineTemplate, **null)

    render_template = False
    @property
    def render_template(self):
        if self.template:
            return self.template.get_template()
        return "resource/list.html"

class CategoryPlugin(CMSPlugin):
    limit    = PositiveIntegerField(_('Number of items'))
    source   = ForeignKey(Category)
    template = ForeignKey(InlineTemplate, **null)

    render_template = False
    @property
    def render_template(self):
        if self.template:
            return self.template.get_template()
        return "resource/list.html"

