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
Models for resource system, provides license, categories and resource downloads.
"""

import gzip
import sys
import os

from django.db.models import *
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.core.files.images import get_image_dimensions
from django.core.validators import MaxLengthValidator
from django.contrib.auth import get_user_model
from django.conf import settings
from person.models import Team

from model_utils.managers import InheritanceManager

from pile.fields import ResizedImageField
from .utils import syntaxer, MimeType, upto, cached, text_count, svg_coords, video_embed, gpg_verify, hash_verify
from .slugify import set_slug

from uuid import uuid4

# Thread-safe current user middleware getter.
from cms.utils.permissions import get_current_user as get_user

null = dict(null=True, blank=True)

__all__ = ('License', 'Category', 'Resource', 'ResourceFile', 'ResourceMirror',
           'Gallery', 'Vote', 'Quota', 'GalleryPlugin', 'CategoryPlugin', 'Tag')

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

    selectable = BooleanField(default=True,
        help_text=_("This license can be selected by all users when uploading."))
    filterable = BooleanField(default=True,
        help_text=_("This license can be used as a filter in gallery indexes."))

    replaced = ForeignKey("License", verbose_name=_('Replaced by'), **null)

    class Meta:
        db_table = 'resource_license'

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

    selectable = BooleanField(default=True,
        help_text=_("This category can be selected by all users when uploading."))
    filterable = BooleanField(default=True,
        help_text=_("This category can be used as a filter in gallery indexes."))

    acceptable_licenses = ManyToManyField(License, db_table='resource_category_acceptable_licenses')

    start_contest = DateField(blank=True, null=True,
       help_text="If specified, this category will have special voting rules.")
    end_contest = DateField(**null)

    def __str__(self):
        return self.name.encode('utf8')

    @property
    def votes(self):
        """Returns a queryset of Votes for this category"""
        return Vote.objects.filter(resource__category=self)

    @property
    def value(self):
        return slugify(self.name)

    def get_absolute_url(self):
        return reverse('resources', kwargs={'category': self.value})


class Tag(Model):
    name     = CharField(max_length=16)
    parent   = ForeignKey('self', related_name='children', **null)
    
    def __unicode__(self):
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
        obj = self.parent
        if isinstance(obj, get_user_model()):
            return reverse('resources', kwargs={'username': obj.username})
        elif isinstance(obj, Group):
            return reverse('resources', kwargs={'team': obj.team.slug})
        return reverse('resources')

    def for_user(self, user):
        return self.get_queryset().filter(Q(user=user.id) | Q(published=True))

    def subscriptions(self):
        """Returns a queryset of users who get alerts for new resources"""
        subs = ResourceFile.subscriptions
        if 'user' in self.core_filters:
            subs.target = self.core_filters['user']
        return subs.all()

    def downloads(self):
        return self.get_queryset().aggregate(Sum('downed')).values()[0]

    def views(self):
        return self.get_queryset().aggregate(Sum('viewed')).values()[0]

    def likes(self):
        return self.get_queryset().aggregate(Sum('liked')).values()[0]

    def new(self):
        return self.get_queryset().filter(category__isnull=True)

    def trash(self):
        return self.get_queryset().filter(gallery__isnull=True).exclude(category=Category.objects.get(pk=1))

    def pastes(self):
        return self.get_queryset().filter(category=Category.objects.get(pk=1))

    def disk_usage(self):
        # This could be done better by storing the file sizes
        return sum(f.resourcefile.download.size for f in self.get_queryset().filter(resourcefile__isnull=False) if f.resourcefile.download and os.path.exists(f.resourcefile.download.path))

    def latest(self):
        user = get_user()
        return self.for_user(user).exclude(category=Category.objects.get(pk=1)).order_by('-created')[:4]


class GroupGalleryManager(ResourceManager):
    def __init__(self, instance):
        super(GroupGalleryManager, self).__init__()
        self.instance = instance

    def get_queryset(self):
        qs = super(GroupGalleryManager, self).get_queryset()
        return qs.filter(galleries__group=self.instance)

    @property
    def parent(self):
        return self.instance

Group.resources = property(lambda self: GroupGalleryManager(self))


class InheritedResourceManager(InheritanceManager, ResourceManager):
    pass


class Resource(Model):
    is_file   = False
    user      = ForeignKey(settings.AUTH_USER_MODEL, related_name='resources', default=get_user)
    name      = CharField(max_length=64)
    slug      = SlugField(max_length=70)
    desc      = TextField(_('Description'), validators=[MaxLengthValidator(50192)], **null)
    category  = ForeignKey(Category, related_name='items', **null)
    tags      = ManyToManyField(Tag, related_name='resources', blank=True)

    created   = DateTimeField(**null) 
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

    class Meta:
        get_latest_by = 'created'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name.encode('utf8')

    def summary_string(self):
        return _("%(file_title)s by %(file_author)s (%(years)s)") \
                  % {'file_title': self.name, 'file_author': self.user, 'years': self.years}
      
    @property
    def parent(self):
        galleries = self.galleries.all()
        if galleries:
            return galleries[0]
        return self.user.resources

    def description(self):
        if not self.desc:
            return '-'
        if '[[...]]' in self.desc:
            return self.desc.split('[[...]]')[0]
        return self.desc[:1000]

    def read_more(self):
        if not self.desc:
            return False
        return len(self.desc) > 1000 or '[[...]]' in self.desc

    def save(self, **kwargs):
        signal = False
        if not self.created and self.published:
            self.created = now()
            signal = True

        set_slug(self)
        ret = super(Resource, self).save(**kwargs)

        if signal:
            from .alert import post_publish
            post_publish.send(sender=Resource, instance=self)

        return ret

    def find_media_type(self):
        # We don't know how to find it for links yet.
        return None

    def find_media_coords(self):
        return (None, None)

    def get_absolute_url(self):
        if self.category_id and self.category_id == 1:
            return reverse('pasted_item', args=[str(self.pk)])
        if self.slug:
            return reverse('resource', kwargs={'username': self.user.username, 'slug': self.slug})
        return reverse('resource', kwargs={'pk': self.pk})

    @property
    def years(self):
        if self.created and self.created.year != self.edited.year:
            return "%d-%d" % (self.created.year, self.edited.year)
        return str(self.edited.year)

    # for counting detail views
    def set_viewed(self, session):
        if session.session_key is not None:
            # We check for session key because it might not exist if this
            # was called from the first view or cookies are blocked.
            (view, is_new) = self.views.get_or_create(session=session.session_key)
            return is_new
        return None

    def is_visible(self):
        return get_user().pk == self.user_id or self.published

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
            @property
            def url(self):
                return self.link
            @property
            def path(self):
                return '/'.join(self.link.split('/')[3:])
        if self.link:
            return NotLocalDownload(self.link)
        return None

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

    signature  = FileField(_('Signature/Checksum'), **upto('sigs'))
    verified   = BooleanField(default=False)
    mirror     = BooleanField(default=False)
    embed      = BooleanField(default=False)

    objects   = ResourceManager()

    ENDORSE_NONE = 0
    ENDORSE_HASH = 1
    ENDORSE_SIGN = 5
    ENDORSE_AUTH = 10

    def save(self, *args, **kwargs):
        if self.download and not self.download._committed:
            if self.pk:
                ResourceRevision.from_resource(self)
            # We might be able to detect that the download has changed here.
            if self.mime().is_raster():
                self.thumbnail.save(self.download.name, self.download, save=False)
            elif self.thumbnail:
                self.thumbnail = None

            self.verified = False
            self.edited = now()
            delattr(self, '_mime')
            self.media_type = self.find_media_type()
            (self.media_x, self.media_y) = self.find_media_coords()

        elif self.signature and not self.signature._committed:
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
        return Resource.is_visible(self) and self.is_available()

    def is_available(self):
        return os.path.exists(self.download.path)

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

    def icon_only(self):
        return Resource.icon(self)

    def as_lines(self):
        """Returns the contents as text"""
        return syntaxer(self.as_text(), self.mime())

    def as_line_preview(self):
        """Returns a few lines of text"""
        return syntaxer(self.as_text(20), self.mime())

    def as_text(self, lines=None):
        if self.mime().is_text() or 'svg' in str(self.mime()):
            text = self.download.file
            text.open()
            text.seek(0)
            # GZip magic number for svgz files.
            if text.peek(2) == '\x1f\x8b':
                text = gzip.GzipFile(fileobj=text)
            if lines is not None:
                return "".join(next(text.file) for x in xrange(lines))
            return text.read().decode('utf-8')
        return "Not text!"


class ResourceRevision(Model):
    """When a resource gets edited and the file is changed, the old file ends up here."""
    resource   = ForeignKey(ResourceFile, related_name='revisions')
    download   = FileField(_('Consumable File'), **upto('file', blank=False))
    signature  = FileField(_('Signature/Checksum'), **upto('sigs'))
    created    = DateTimeField(auto_now=True)
    version    = IntegerField(default=0)

    def __str__(self):
        return "Version %d" % self.version

    def save(self, commit=True, **kw):
        if not self.pk:
            self.version = ResourceRevision.objects.filter(resource_id=self.resource.pk).count() + 1
        super(ResourceRevision, self).save(**kw)

    @classmethod
    def from_resource(cls, resource):
        kw = ResourceFile.objects.filter(pk=resource.pk).values('download', 'signature')[0]
        if kw['download'] != resource.download.name:
            kw['resource'] = resource
            obj = cls(**kw)
            obj.save()
            return obj


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
    manager  = ForeignKey(settings.AUTH_USER_MODEL, default=get_user)
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
        return reverse('mirror', kwargs={'slug': self.uuid})

    @staticmethod
    def resources():
        """List of all mirrored resources"""
        return ResourceFile.objects.filter(mirror=True)      

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
        return "Mirror '%s' from '%s'" % \
                (self.name.encode('utf8'), self.host.encode('utf8'))


class GalleryManager(Manager):
    def for_user(self, user):
        return self.get_queryset().filter(Q(user=user.id) | Q(items__published=True)).distinct()


class Gallery(Model):
    GALLERY_STATUSES = (
      (None, 'No Status'),
      (' ', 'Casual Wish'),
      ('1', 'Draft'),
      ('2', 'Proposal'),
      ('3', 'Reviewed Proposal'),
      ('+', 'Under Development'),
      ('=', 'Complete'),
      ('-', 'Rejected'),
    )
    user      = ForeignKey(settings.AUTH_USER_MODEL, related_name='galleries', default=get_user)
    group     = ForeignKey(Group, related_name='galleries', **null)
    name      = CharField(max_length=64)
    slug      = SlugField(max_length=70)
    desc      = TextField(_('Description'), validators=[MaxLengthValidator(50192)], **null)
    thumbnail = ForeignKey(Resource, help_text=_('Which resource should be the thumbnail for this gallery'), **null)
    status    = CharField(max_length=1, db_index=True, choices=GALLERY_STATUSES, **null)

    items     = ManyToManyField(Resource, related_name='galleries', blank=True)

    objects   = GalleryManager()

    def __unicode__(self):
        if self.group:
            return _(u"%(gallery_name)s (for group %(group_name)s)") \
                  % {'gallery_name': self.name, 'group_name': unicode(self.group)}
        return  _(u"%(gallery_name)s (by %(user_name)s)") \
                  % {'gallery_name': self.name, 'user_name': unicode(self.user)}

    def __str__(self):
        return unicode(self).encode('utf8')

    def save(self, *args, **kwargs):
        set_slug(self)
        super(Gallery, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.group:
            try:
              return reverse('resources', kwargs={
                'team': self.group.team.slug,
                'galleries': self.slug,
              })
            except Team.DoesNotExist:
                pass
        elif self.slug:
            return reverse('resources', kwargs={
              'username': self.user.username,
              'galleries': self.slug,
            })
        return reverse('resources', kwargs={'gallery_id': self.pk})

    @property
    def value(self):
        return self.slug

    @property
    def parent(self):
        if self.group:
            return self.group.resources
        return self.user.resources

    def is_visible(self):
        return self.items.for_user(get_user()).count() or self.is_editable()

    def is_editable(self):
        user = get_user()
        return user and (not user.id is None) and (
            self.user == user or user.is_superuser \
              or (user.groups.count() and self.group in user.groups.all()))

    def icon(self):
        if self.thumbnail:
            return self.thumbnail.icon()
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
        return Resource.objects.filter(published=True, **f)


class Vote(Model):
    """Vote for a resource in some way"""
    resource = ForeignKey(Resource, related_name='votes')
    voter    = ForeignKey(settings.AUTH_USER_MODEL, related_name='favorites')

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
    group    = OneToOneField(Group, related_name='quotas', **null)
    size     = IntegerField(_("Quota Size (KiB)"), default=1024)

    def __str__(self):
        return str(self.group)

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
        return "resources/resource_%s.html" % (self.display or 'list')

class CategoryPlugin(CMSPlugin):
    limit    = PositiveIntegerField(_('Number of items per page'))
    source   = ForeignKey(Category)
    display  = CharField(_("Display Style"), max_length=32, choices=DISPLAYS, **null)

    @property
    def render_template(self):
        return "resources/resource_%s.html" % (self.display or 'list')

