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


from inkscape.settings import DESIGN_URL, MAX_PREVIEW_SIZE
from inkscape.fields import ResizedImageField


null = dict(null=True, blank=True)
def upto(d, c='resources', blank=True, lots=False):
    dated = lots and ["%Y","%m"] or []
    return dict(null=blank, blank=blank, upload_to=os.path.join(c, d, *dated))

def get_mime(path):
    return (mimetypes.guess_type(path, True)[0] or 'text/plain').split('/')

def get_file_type(path):
    mime = get_mime(path)
    if mime[0] in ['image']:
        return mime[0]
    if mime[1][-2:] == 'ml':
        return 'xml'
    if 'zip' in mime[1] or 'compressed' in mime[1] or 'tar' in mime[1]:
        return 'archive'
    if mime[0] in ['text','application']:
        if 'opendocument' in mime[1]:
            return mime[1].split('.')[-1]
        return mime[1]
    return mime[0];


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


class ResourceManager(Manager):
    def get_query_set(self):
        return Manager.get_query_set(self).order_by('-created')

    def for_user(self, user):
        return self.get_query_set().filter(Q(user=user.id) | Q(published=True))

    def downloads(self):
        return self.get_query_set().aggregate(Sum('downed')).values()[0]

    def views(self):
        return self.get_query_set().aggregate(Sum('viewed')).values()[0]


class Resource(Model):
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

    objects   = ResourceManager()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('resource', args=[str(self.id)])

    def is_visible(self, user):
        return user == self.user or self.published

    def years(self):
        if self.created.year != self.edited.year:
            return "%d-%d" % (self.created.year, self.edited.year)
        return "%d" % self.edited.year

    def is_new(self):
        return not (self.desc and self.published and self.category)

    def save(self, *args, **kwargs):
        self.edited = now()
        return Model.save(self, *args, **kwargs)

    def is_file(self):
        return type(self.outer) is ResourceFile

    @property
    def gallery(self):
        return self.gallery_set.all()[0]

    def icon(self):
        """Returns a 150px icon either from the thumbnail, the image itself or the mimetype"""
        if self.thumbnail:
            return self.thumbnail.url
        return self.outer.icon() or os.path.join(DESIGN_URL, 'mime', 'unknown.svg')

    @property
    def outer(self):
        if type(self) is Resource:
            if hasattr(self, 'resourcefile'):
                return self.resourcefile
            elif hasattr(self, 'resourceurl'):
                return self.resourceurl
        return self


class ResourceFile(Resource):
    """This is a resource with an uploaded file"""
    download = FileField(_('Consumable File'), **upto('file', blank=False))

    license   = ForeignKey(License, **null)
    owner     = BooleanField(_('I own this work'), default=True)

    def download_url(self):
        return self.download.url

    def is_image(self):
        """Returns true if the download is an image (svg/png/jpeg/gif)"""
        return get_file_type(self.download.path) == 'image'

    def save(self, *args, **kwargs):
        Resource.save(self, *args, **kwargs)
        if self.download and not self.thumbnail:
            mime = get_mime(self.download.path)
            if mime[0] == 'image' and mime[1] in ['jpeg','gif','png']:
                self.thumbnail.save(self.download.name, self.download)
            Resource.save(self, *args, **kwargs)

    def icon(self):
        if not self.download:
            return None
        mime = get_file_type(self.download.path)
        if mime == 'image' and self.download.size < MAX_PREVIEW_SIZE:
            return self.download.url
        return os.path.join(DESIGN_URL, 'mime', mime + '.svg')


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


class ResourceUrl(Resource):
    """This is a resource that links to somewhere else"""
    download = URLField(_('Consumable File'), **null)
    source   = URLField(_('Source File'), **null)

    def download_url(self):
        return self.download

    def source_url(self):
        return self.source



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


