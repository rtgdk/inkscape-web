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
import mimetypes

from django.db.models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.utils.timezone import now
from django.core.urlresolvers import reverse

from model_utils.managers import InheritanceManager

from inkscape.settings import DESIGN_URL, DESIGN_ROOT, MAX_PREVIEW_SIZE
from inkscape.fields import ResizedImageField

from .utils import syntaxer

null = dict(null=True, blank=True)
def upto(d, c='resources', blank=True, lots=False):
    dated = lots and ["%Y","%m"] or []
    return dict(null=blank, blank=blank, upload_to=os.path.join(c, d, *dated))


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

    replaced = ForeignKey("License", verbose_name=_('Replaced by'), **null)

    def is_free(self):
        return not self.nc and not self.nd and not arr

    def is_all_rights(self):
        return self.nc and self.nd and not self.at

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)


class Category(Model):
    name     = CharField(max_length=64)
    desc     = TextField(**null)

    acceptable_licenses = ManyToManyField(License)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_resources', args=[str(self.id)])


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

    link      = URLField(_('More Info URL'), **null)
    viewed    = IntegerField(default=0)
    downed    = IntegerField(_('Downloaded'), default=0)

    media_type = CharField(_('File Type'), max_length=64, **null)

    objects   = ResourceManager()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.edited = now()
        # This might need a save to work right??
        self.media_type = mimetypes.guess_type(self.download.path, True)[0] or 'text/plain'
        return Model.save(self, *args, **kwargs)

    def get_absolute_url(self):
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
        return not self.desc

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

    def icon(self):
        """Returns a 150px icon either from the thumbnail, the image itself or the mimetype"""
        if self.thumbnail:
            return self.thumbnail.url
        for ft_icon in [self.file_type, self.is_text and 'plain' or 'unknown']: 
            if os.path.exists(os.path.join(DESIGN_ROOT,'mime',ft_icon+'.svg')):
                break
        return os.path.join(DESIGN_URL, 'mime', ft_icon+'.svg')

    def banner(self):
        for ft_icon in [self.file_subtype, 'unknown']:
            if os.path.exists(os.path.join(DESIGN_ROOT,'mime','banner',ft_icon+'.svg')):
                break
        return os.path.join(DESIGN_URL, 'mime','banner',ft_icon+'.svg')

    @property
    def mime(self):
        return self.media_type.split('/')

    @property
    def file_subtype(self):
        return self.mime[1].split('+')[0]

    @property
    def file_type(self):
        mime = self.mime
        if mime[0] in ['image']:
            return mime[0]
        if mime[1][-2:] == 'ml':
            return 'xml'
        if 'zip' in mime[1] or 'compressed' in mime[1] or 'tar' in mime[1]:
            return 'archive'
        if mime[0] in ['text','application']:
            if 'opendocument' in mime[1]:
                return mime[1].split('.')[-1]
            if mime[1][:2] == 'x-':
                return mime[1][2:]
            return mime[1]
        return 'unknown'

    @property
    def is_text(self):
        return self.mime[0] == 'text' or self.mime[1] == 'javascript'

    @property
    def is_image(self):
        return self.file_type == 'image'

    @property
    def is_raster(self):
        return self.is_image and self.mime[1] in ['jpeg', 'gif', 'png']

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



class ResourceFile(Resource):
    """This is a resource with an uploaded file"""
    is_file = True

    download   = FileField(_('Consumable File'), **upto('file', blank=False))

    license    = ForeignKey(License, **null)
    owner      = BooleanField(_('I own this work'), default=True)

    def save(self, *args, **kwargs):
        Resource.save(self, *args, **kwargs)

        if self.download and not self.thumbnail:
            # We might be able to detect that the download has changed here.
            if self.is_raster:
                self.thumbnail.save(self.download.name, self.download)
            elif self.thumbnail:
                self.thumbnail = None
            Resource.save(self, *args, **kwargs)


    def icon(self):
        if not self.thumbnail and self.is_image and self.download.size < MAX_PREVIEW_SIZE:
            return self.download.url
        return Resource.icon(self)

    def as_text(self):
        """Returns the contents as text"""
        if self.is_text:
            with open(self.download.path, 'r') as fhl:
                text = fhl.read()
                return [ (range(1,text.count("\n")), syntaxer(text)) ]
        return "Not text!"


class GalleryManager(Manager):
    def for_user(self, user):
        return self.get_query_set().filter(Q(user=user.id) | Q(items__published=True)).distinct()


class Gallery(Model):
    user      = ForeignKey(User, related_name='galleries')
    name      = CharField(max_length=64)
    items     = ManyToManyField(Resource)

    objects   = GalleryManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gallery', args=[str(self.id)])

    def is_visible(self, user=None):
        return self.user == user or self.items.for_user(user).count()

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


