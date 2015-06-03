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

import sys
import os

from django.db.models import *
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.core.files.images import get_image_dimensions
from django.core.validators import MaxLengthValidator
from django.conf import settings

from model_utils.managers import InheritanceManager


from pile.fields import ResizedImageField
from .utils import syntaxer, MimeType, upto, cached, text_count, svg_coords, video_embed, gpg_verify, hash_verify
from .signals import post_publish
from .slugify import set_slug

from uuid import uuid4

# Thread-safe current user middleware getter.
from cms.utils.permissions import get_current_user as get_user

null = dict(null=True, blank=True)

__all__ = ('License', 'Category', 'Resource', 'ResourceFile', 'ResourceMirror',
           'Gallery', 'Vote', 'Quota', 'GalleryPlugin', 'CategoryPlugin')

DOMAINS = {
  'inkscape.org': 'Inkscape Website',
  'launchpad.net': 'Launchpad',
  'deviantart.com': 'deviantArt',
  'openclipart.org': 'OpenClipart (OCAL)',
}

class License(Model):
    name    = CharField(max_length=64)
    code    = CharField(max_length=16)
    link    = URLField(**null)
    banner  = FileField(_('License Banner (svg:80x15)'), **upto('banner', 'license'))
    icon    = FileField(_('License Icon (svg:100x40)'), **upto('icon', 'license'))

    at  = BooleanField(_('Attribution'), default=True)
    sa  = BooleanField(_('Copyleft (Share Alike)'), default=False)
    nc  = BooleanField(_('Non-Commercial'), default=False)
    nd  = BooleanField(_('Non-Derivative'), default=False)

    visible  = BooleanField(default=True)
    replaced = ForeignKey("License", verbose_name=_('Replaced by'), **null)

    @property
    def value(self):
        return self.code

    def is_free(self):
        return not self.nc and not self.nd

    def is_all_rights(self):
        return self.nc and self.nd and not self.at

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.code)


class Category(Model):
    name     = CharField(max_length=64)
    desc     = TextField(validators=[MaxLengthValidator(1024)], **null)

    visible  = BooleanField(default=True)
    acceptable_licenses = ManyToManyField(License)

    def __str__(self):
        return str(self.name)

    @property
    def value(self):
        return slugify(self.name)

    def get_absolute_url(self):
        return reverse('resources', kwargs={'category': self.pk})


class Tag(Model):
    name     = CharField(max_length=16)
    parent   = ForeignKey('self', **null)
    
    def __str__(self):
        return self.name


class ResourceManager(Manager):
    def breadcrumb_name(self):
        return _("InkSpaces")

    @property
    def parent(self):
        if 'user__exact' in self.core_filters: 
            return self.core_filters['user__exact']
        try:
            return self.get_queryset().latest('published').user
        except Resource.DoesNotExist:
            return None

    def get_absolute_url(self):
        if self.parent:
            return reverse('resources', kwargs={'username': self.parent.username})
        return reverse('resources')

    def for_user(self, user):
        return self.get_queryset().filter(Q(user=user.id) | Q(published=True))

    def downloads(self):
        return self.get_queryset().aggregate(Sum('downed')).values()[0]

    def views(self):
        return self.get_queryset().aggregate(Sum('viewed')).values()[0]

    def new(self):
        return self.get_queryset().filter(category__isnull=True)

    def trash(self):
        return self.get_queryset().filter(gallery__isnull=True).exclude(category=Category.objects.get(pk=1))

    def pastes(self):
        return self.get_queryset().filter(category=Category.objects.get(pk=1))

    def disk_usage(self):
        # This could be done better by storing the file sizes
        return sum(f.download.size for f in self.get_queryset().filter(resourcefile__isnull=False) if os.path.exists(f.download.path))

    def latest(self):
        return self.get_queryset().exclude(category=Category.objects.get(pk=1)).order_by('created')[:4]


class InheritedResourceManager(InheritanceManager, ResourceManager):
    def get_queryset(self):
        return InheritanceManager.get_queryset(self)\
            .select_subclasses('resourcefile').order_by('-created')


class Resource(Model):
    is_file   = False
    user      = ForeignKey(User, related_name='resources', default=get_user)
    name      = CharField(max_length=64)
    slug      = SlugField(max_length=70)
    desc      = TextField(_('Description'), validators=[MaxLengthValidator(50192)], **null)
    category  = ForeignKey(Category, related_name='items',
                  limit_choices_to={'visible': True}, **null)
    tags      = ManyToManyField(Tag, related_name='resources', **null)

    created   = DateTimeField(**null) # Start of copyright, when 'published=True'
    edited    = DateTimeField(**null) # End of copyright, last file-edit/updated.
    published = BooleanField(default=False)

    thumbnail = ResizedImageField(_('Thumbnail'), 190, 190, **upto('thumb'))

    link      = URLField(_('External Link'), **null)
    liked     = PositiveIntegerField(default=0)
    viewed    = PositiveIntegerField(default=0)
    downed    = PositiveIntegerField(_('Downloaded'), default=0)
    fullview  = PositiveIntegerField(_('Full Views'), default=0)

    media_type = CharField(_('File Type'), max_length=64, **null)
    media_x    = IntegerField(**null)
    media_y    = IntegerField(**null)

    objects   = InheritedResourceManager()

    def __unicode__(self):
        return self.name

    @property
    def parent(self):
        galleries = self.galleries.all()
        if galleries:
            return galleries[0]
        return self.user.resources

    def description(self):
        if '[[...]]' in self.desc:
            return self.desc.split('[[...]]')[0]
        return self.desc[:1000]

    def read_more(self):
        return len(self.desc) > 1000 or '[[...]]' in self.desc

    def save(self, *args, **kwargs):
        if self.has_file_changed():
            self.edited = now()
            delattr(self, '_mime')
            self.media_type = self.find_media_type()
            (self.media_x, self.media_y) = self.find_media_coords()

        if not self.created and self.published:
            self.created = now()
            post_publish.send(sender=Resource, instance=self)

        set_slug(self)
        return Model.save(self, *args, **kwargs)

    def has_file_changed(self):
        return False

    def find_media_type(self):
        # We don't know how to find it for links yet.
        return None

    def find_media_coords(self):
        return (None, None)

    def get_absolute_url(self):
        if self.category and self.category.id == 1:
            return reverse('pasted_item', args=[str(self.id)])
        return reverse('resource', kwargs={'username': self.user.username, 'slug': self.slug})

    @property
    def years(self):
        if self.created.year != self.edited.year:
            return "%d-%d" % (self.created.year, self.edited.year)
        return str(self.edited.year)

    def set_viewed(self, session):
        if session.session_key is not None:
            # We check for session key because it might not exist if this
            # was called from the first view or cookies are blocked.
            (view, is_new) = self.views.get_or_create(session=session.session_key)
            return is_new
        return None

    def is_visible(self):
        return get_user() == self.user or self.published

    def voted(self):
        return self.votes.for_user(get_user()).first()

    @property
    def is_new(self):
        return not self.category

    @property
    def is_video(self):
        return bool(self.video)

    @property
    def video(self):
        return video_embed(self.link)

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
            return self.galleries.all()[0]
        except IndexError:
            return None

    @cached
    def mime(self):
        """Returns an encapsulated media_type as a MimeType object"""
        return MimeType( self.media_type or 'application/unknown' )

    def link_from(self):
        """Returns the domain name or useful name if known for link"""
        try:
            domain = '.'.join(self.link.split("/")[2].split('.')[-2:])
            return DOMAINS.get(domain, domain)
        except Exception:
            return 'unknown'

    def icon(self):
        """Returns a 150px icon either from the thumbnail, the image itself or the mimetype"""
        if self.thumbnail and os.path.exists(self.thumbnail.path):
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

    license    = ForeignKey(License, limit_choices_to={'visible': True}, **null)
    owner      = BooleanField(_('Permission'), choices=OWNS, default=True)

    signature  = FileField(_('Signature/Checksum'), **upto('sigs'))
    verified   = BooleanField(default=False)
    mirror     = BooleanField(default=False)

    objects   = ResourceManager()

    ENDORSE_NONE = 0
    ENDORSE_HASH = 1
    ENDORSE_SIGN = 5
    ENDORSE_AUTH = 10

    def save(self, *args, **kwargs):
        if self.download and self.has_file_changed():
            # We might be able to detect that the download has changed here.
            if self.mime().is_raster():
                self.thumbnail.save(self.download.name, self.download, save=False)
            elif self.thumbnail:
                self.thumbnail = None
        if self.has_file_changed() or (self.signature and not self.signature._committed):
            self.verified = False
        Resource.save(self, *args, **kwargs)

    def filename(self):
        return os.path.basename(self.download.name)

    def signature_type(self):
        return self.signature.name.rsplit('.', 1)[-1]

    def _verify(self, _type):
        if _type == 'sig': # GPG Signature
            return gpg_verify(self.user, self.signature, self.download)
        return hash_verify(_type, self.signature, self.download)

    def endorsement(self):
        if not self.signature:
            return self.ENDORSE_NONE
        sig_type = self.signature_type()
        if not self.verified:
            self.verified = self._verify(sig_type)
            self.save()
        if self.verified and sig_type == 'sig':
            if self.user.has_perm('resource.change_resourcemirror'):
                return self.ENDORSE_AUTH
            return self.ENDORSE_SIGN
        return self.verified and self.ENDORSE_HASH or self.ENDORSE_NONE

    def is_visible(self):
        return Resource.is_visible(self) and os.path.exists(self.download.path)

    def has_file_changed(self):
        return not self.download._committed

    def find_media_type(self):
        """Returns the media type of the downloadable file"""
        return str(MimeType(filename=self.download.path))

    def find_media_coords(self):
        if self.mime().is_raster():
            return get_image_dimensions(self.download.file)
        elif self.mime().is_image():
            return svg_coords(self.as_text())
        elif self.mime().is_text():
            try:
                return text_count(self.as_text())
            except UnicodeDecodeError:
                # Text file is corrupt, treat it as a binary
                self.media_type = 'application/octet-stream'
        return (None, None)

    def icon(self):
        if not self.thumbnail and self.mime().is_image():
            if os.path.exists(self.download.path) \
              and self.download.size < settings.MAX_PREVIEW_SIZE:
                return self.download.url
        return Resource.icon(self)

    def as_lines(self):
        """Returns the contents as text"""
        return syntaxer(self.as_text(), self.mime())

    def as_text(self):
        if self.mime().is_text() or 'svg' in str(self.mime()):
            self.download.file.open()
            self.download.file.seek(0)
            return self.download.file.read().decode('utf-8')
        return "Not text!"


class MirrorManager(Manager):
    def select_mirror(self, update=None):
        """Selects the next best mirror randomly from the mirror pool"""
        query = self.get_queryset().filter(chk_return=200)
        if update:
            query = query.filter(sync_time__gte=update)
        # Attempt to weight the mirrors (needs CS review)
        import random
        total = sum(mirror.capacity for mirror in query)
        compare = random.uniform(0, total)
        upto = 0
        for mirror in query:
            if upto + mirror.capacity > compare:
                return mirror
            upto += mirror.capacity
        return None



class ResourceMirror(Model):
    uuid     = CharField(_("Unique Identifier"), max_length=64, default=uuid4)
    name     = CharField(max_length=64)
    manager  = ForeignKey(User, default=get_user)
    url      = URLField(_("Full Base URL"))
    capacity = PositiveIntegerField(_("Capacity (MB/s)"))
    created  = DateTimeField(default=now)

    sync_time  = DateTimeField(**null)
    sync_count = PositiveIntegerField(default=0)

    chk_time   = DateTimeField(_("Check Time Date"), **null)
    chk_return = IntegerField(_("Check Returned HTTP Code"), **null)

    objects = MirrorManager()

    @property
    def host(self):
        return self.url.split('/')[2]

    def get_absolute_url(self):
        return reverse('mirror', kwargs={'uuid': self.uuid})

    def do_sync(self):
        self.sync_time = now()
        self.sync_count += 1
        return self.save()

    def do_check(self):
        raise NotImplementedError("Mirror Checking Not available yet.")
        self.chk_return = 200
        self.chk_time   = now()
        self.save()

    def get_url(self, item):
        filename = os.path.basename(item.download.name)
        return os.path.join(self.url, 'file', filename)

    def __str__(self):
        return "Mirror '%s' from '%s'" % (self.name, self.host)


class GalleryManager(Manager):
    def for_user(self, user):
        return self.get_queryset().filter(Q(user=user.id) | Q(items__published=True)).distinct()


class Gallery(Model):
    user      = ForeignKey(User, related_name='galleries', default=get_user)
    group     = ForeignKey(Group, related_name='galleries', **null)
    name      = CharField(max_length=64)
    slug      = CharField(max_length=70)
    items     = ManyToManyField(Resource, related_name='galleries', **null)

    objects   = GalleryManager()

    def __unicode__(self):
        if self.group:
            return self.name + " [" + unicode(_('for group')) + " " + str(self.group) + "]"
        return self.name + " (" + unicode(_('by')) + " " + str(self.user) + u")"

    def save(self, *args, **kwargs):
        set_slug(self)
        super(Gallery, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('resources', kwargs={
          'username': self.user.username,
          'galleries': self.slug,
        })

    @property
    def value(self):
        return self.slug

    @property
    def parent(self):
        if self.group:
            return self.group
        return self.user.resources

    def is_visible(self):
        return self.items.for_user(get_user()).count() or self.is_editable()

    def is_editable(self):
        user = get_user()
        return user and (not user.id is None) and (
            self.user == user or user.is_superuser \
              or (user.groups.count() and self.group in user.groups.all()))

    def icon(self):
        for item in self.items.all():
            if item.is_visible():
                return item.icon()
        return os.path.join(settings.STATIC_URL, 'images', 'folder.svg')

    def __len__(self):
        return self.items.count()


class VoteManager(Manager):
    def count(self):
        return self.get_queryset().count()

    def for_user(self, user):
        return self.get_queryset().filter(Q(voter=user.id))

    def items(self):
        f = dict( ('votes__'+a,b) for (a,b) in self.core_filters.items() )
        return Resource.objects.filter(**f)


class Vote(Model):
    """Vote for a resource in some way"""
    resource = ForeignKey(Resource, related_name='votes')
    voter    = ForeignKey(User, related_name='favorites')

    objects = VoteManager()
    
    def save(self, **kwargs):
        ret = super(Vote, self).save(**kwargs)
        self.resource.liked = self.resource.votes.count()
        self.resource.save()
        return ret

    def delete(self):
        ret = super(Vote, self).delete()
        self.resource.liked = self.resource.votes.count()
        self.resource.save()
        return ret


class Views(Model):
    """Record the view of an item"""
    resource = ForeignKey(Resource, related_name='views')
    session  = CharField(max_length=40)

    def save(self, **kwargs):
        ret = super(Views, self).save(**kwargs)
        self.resource.viewed = self.resource.views.count()
        self.resource.save()
        return ret


class Quota(Model):
    group    = ForeignKey(Group, related_name='quotas', unique=True, **null)
    size     = IntegerField(_("Quota Size (KiB)"), default=1024)

    def __str__(self):
        return str(self.group)

def quota_for_user(user):
    groups = Q(group__in=user.groups.all()) | Q(group__isnull=True)
    quotas = Quota.objects.filter(groups)
    if quotas.count():
        return quotas.aggregate(Max('size'))['size__max'] * 1024
    return 0

User.quota = quota_for_user

# ------------- Alerts ------------ #

from alerts.models import *

class ResourceAlert(EditedAlert):
    name     = _("New Gallery Resource")
    desc     = _("An alert is sent when the target user submits a resource.")
    category = CATEGORY_USER_TO_USER
    sender   = Resource

    subject       = _("New submission: ") + "{{ instance }}"
    email_subject = _("New submission: ") + "{{ instance }}"
    default_email = False
    signal        = post_publish

    # We subscribe to the user of the instance, not the instance.
    target = 'user'

    def call(self, sender, **kwargs):
        return super(ResourceAlert, self).call(sender, **kwargs)

register_alert('user_gallery', ResourceAlert)


# ------------- CMS ------------ #

from cms.models import CMSPlugin

DISPLAYS = (
  ('list', _("Gallery List")),
  ('rows', _("Gallery Rows")),
)

class GalleryPlugin(CMSPlugin):
    limit    = PositiveIntegerField(_('Number of items per page'))
    source   = ForeignKey(Gallery)
    display  = CharField(_("Display Style"), max_length=32, choices=DISPLAYS, **null)

    @property
    def render_template(self):
        return "cms/plugins/resource-%s.html" % (self.display or 'list')

class CategoryPlugin(CMSPlugin):
    limit    = PositiveIntegerField(_('Number of items per page'))
    source   = ForeignKey(Category)
    display  = CharField(_("Display Style"), max_length=32, choices=DISPLAYS, **null)

    @property
    def render_template(self):
        return "cms/plugins/resource-%s.html" % (self.display or 'list')



