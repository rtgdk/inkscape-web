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

__all__ = ('License', 'Category', 'Resource', 'ResourceMirror',
           'Gallery', 'Vote', 'Quota', 'GalleryPlugin', 'CategoryPlugin',
           'Tag', 'TagCategory')

import gzip
import sys
import os

from django.db.models import *
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator
from django.contrib.auth import get_user_model
from django.conf import settings
from person.models import Team

from pile.fields import ResizedImageField
from .slugify import set_slug
from .utils import *

from uuid import uuid4

# Thread-safe current user middleware getter.
from cms.utils.permissions import get_current_user as get_user

null = dict(null=True, blank=True)

OWNS = (
  (None, _('No permission')),
  (True, _('I own the work')),
  (False, _('I have permission')),
)

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
    name   = CharField(max_length=128)
    slug   = SlugField(max_length=128)
    desc   = TextField(validators=[MaxLengthValidator(1024)], **null)
    symbol = FileField(_('Category Icon (svg:128x128)'), **upto('icon', 'category'))
    groups = ManyToManyField(Group, blank=True,
        help_text=_("The category is restricted to these groups only."))

    selectable = BooleanField(default=True,
        help_text=_("This category is not private/hidden from all users."))

    filterable = BooleanField(default=True,
        help_text=_("This category can be used as a filter in gallery indexes."))
    
    acceptable_licenses = ManyToManyField(License, db_table='resource_category_acceptable_licenses')

    acceptable_media_x = CharField(max_length=255, blank=True, null=True)
    acceptable_media_y = CharField(max_length=255, blank=True, null=True)
    acceptable_types = CharField(max_length=255, blank=True, null=True)
    acceptable_size = CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name.encode('utf8')

    def save(self, **kwargs):
        set_slug(self)
        super(Category, self).save(**kwargs)

    @property
    def parent(self):
        return getattr(self, '_parent', Resource.objects.all())

    @property
    def value(self):
        return self.slug
    
    @property
    def icon(self):
        if self.symbol:
            return self.symbol.url 
        return static('images', 'no-category.svg')

    def thumbnail_url(self):
        return self.icon

    def get_absolute_url(self):
        kw = {'category': self.slug}
        if hasattr(self, 'parent'):
            user = getattr(self.parent, "parent", None)
            if isinstance(user, get_user_model()):
                kw['username'] = user.username
        return reverse('resources', kwargs=kw)


class TagQuerySet(QuerySet):
    def as_cloud(self, link, size=10):
        result = []
        qs = self.annotate(count=Count(link)).values_list('name', 'count')
        tags = dict(qs.order_by('-count')[0:size])
        if tags:
            maximum = float(max(tags.values()))
            for name in sorted(tags):
                result.append((name, int(tags[name] / maximum * 6)))
        return result


class Tag(Model):
    name     = CharField(max_length=16, unique=True)
    category = ForeignKey('TagCategory', related_name='tags', **null)

    objects  = TagQuerySet.as_manager()

    class Meta:
        ordering = 'name',
    
    def save(self, **kwargs):
        self.name = self.name.lower()
        # we could check here if tag already exists
        ret = super(Tag, self).save(**kwargs)
        return ret
    
    def __unicode__(self):
        return self.name


class TagCategory(Model):
    """Used to classify tag searches and tag clouds."""
    name = CharField(max_length=48)

    categories = ManyToManyField(Category, related_name='tags',
            help_text=_("Only show with these categories"))

    def __unicode__(self):
        return self.name


class ResourceQuerySet(QuerySet):
    def breadcrumb_name(self):
        return _("Resources")

    @property
    def parent(self):
        return self._hints.get('instance', getattr(self, 'instance', None))

    @property
    def votes(self):
        return self.aggregate(Sum('liked'))['liked__sum']

    def get_absolute_url(self):
        obj = self.parent
        if isinstance(obj, get_user_model()):
            return reverse('resources', kwargs={'username': obj.username})
        elif isinstance(obj, Group):
            return reverse('resources', kwargs={'team': obj.team.slug})
        return reverse('resources')


class ResourceManager(Manager):
    def get_queryset(self):
        qs = ResourceQuerySet(self.model, using=self._db)
        qs.query.select_related = True
        return qs

    def for_user(self, user):
        return self.get_queryset().filter(Q(user=user.id) | Q(published=True))

    def subscriptions(self):
        """Returns a queryset of users who get alerts for new resources"""
        subs = Resource.subscriptions
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
        return sum(resource.download.size
            for resource in Resource.objects.filter(pk__in=self.get_queryset())
            if resource.download and os.path.exists(resource.download.path))

    def latest(self, column=None):
        if column:
            return super(ResourceManager, self).latest(column)
        user = get_user()
        return self.for_user(user).exclude(category=Category.objects.get(pk=1)).order_by('-created')[:4]


class GroupGalleryManager(Manager):
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


class Resource(Model):
    """This is a resource with an uploaded file"""
    owner_field = 'user'
    is_resource = True

    ENDORSE_NONE = 0
    ENDORSE_HASH = 1
    ENDORSE_SIGN = 5
    ENDORSE_AUTH = 10

    CONTEST_WINNER = 1
    CONTEST_RUNNER_UP = 2
    EXTRA_CHOICES = (
      (None, _('No extra status')),
      (CONTEST_WINNER, _('Winner')),
      (CONTEST_RUNNER_UP, _('Runner Up')),
    )
    EXTRA_CSS = ['', 'winner', 'runnerup']

    user      = ForeignKey(settings.AUTH_USER_MODEL, related_name='resources', default=get_user)
    name      = CharField(max_length=64)
    slug      = SlugField(max_length=70)
    desc      = TextField(_('Description'), validators=[MaxLengthValidator(50192)], **null)
    category  = ForeignKey(Category, verbose_name=_("Category"), related_name='items', **null)
    tags      = ManyToManyField(Tag, verbose_name=_("Tags"), related_name='resources', blank=True)

    created   = DateTimeField(**null) 
    edited    = DateTimeField(**null) # End of copyright, last file-edit/updated.
    published = BooleanField(default=False)

    thumbnail = ResizedImageField(_('Thumbnail'), 190, 190, **upto('thumb'))
    rendering = ResizedImageField(_('Rendering'), 780, 600, **upto('render'))

    link      = URLField(_('External Link'), **null)
    liked     = PositiveIntegerField(default=0)
    viewed    = PositiveIntegerField(default=0)
    downed    = PositiveIntegerField(_('Downloaded'), default=0)
    fullview  = PositiveIntegerField(_('Full Views'), default=0)

    media_type = CharField(_('File Type'), max_length=128, **null)
    media_x    = IntegerField(**null)
    media_y    = IntegerField(**null)

    extra_status = PositiveSmallIntegerField(choices=EXTRA_CHOICES, **null)
    extra_css = property(lambda self: self.EXTRA_CSS[self.extra_status])

    # ======== ITEMS FROM RESOURCEFILE =========== #
    download   = FileField(_('Consumable File'), **upto('file', blank=True))

    license    = ForeignKey(License, verbose_name=_("License"), **null)
    owner      = BooleanField(_('Permission'), choices=OWNS, default=True)

    signature  = FileField(_('Signature/Checksum'), **upto('sigs'))
    verified   = BooleanField(default=False)
    mirror     = BooleanField(default=False)
    embed      = BooleanField(default=False)

    checked_by = ForeignKey(settings.AUTH_USER_MODEL, related_name='resource_checks', **null)
    checked_sig = FileField(_('Counter Signature'), **upto('sigs'))

    objects   = ResourceManager()

    class Meta:
        get_latest_by = 'created'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name.encode('utf8')

    def summary_string(self):
        return _("%(file_title)s by %(file_author)s (%(years)s)") \
                  % {'file_title': self.name, 'file_author': self.user, 'years': self.years}
      
    @classmethod
    def from_db(cls, db, field_names, values):
        db_instance = super(Resource, cls).from_db(db, field_names, values)
        # cache old value for link
        db_instance._old_link = values[field_names.index('link')]
        return db_instance 
      
    @property
    def parent(self):
        if self.is_pasted:
            cat = self.category
            cat._parent = self.user.resources.all()
            return cat
        galleries = self.galleries.all()
        if galleries:
            return galleries[0]
        return self.user.resources.all()

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
      
        if self.download and not self.download._committed:
            # There is a download file and it has been changed

            if self.pk:
                # Save the old download file in a revision
                ResourceRevision.from_resource(self)

            # It's a raster image file, so regenerate the thumbnail
            if self.mime().is_raster():
                self.thumbnail.save(self.download.name, self.download, save=False)

            self.verified = False
            self.edited = now()
            delattr(self, '_mime')
            try:
                self.media_type = str(self.file.mime)
                (self.media_x, self.media_y) = self.file.media_coords
            except ValueError:
                 # Text file is corrupt, treat it as a binary
                 self.media_type = 'application/octet-stream'

        # the signature on an existing resource has changed
        elif self.signature and not self.signature._committed:
            self.verified = False

        # mark as edited for link-only resources when they are added 
        # or when link changes
        if not self.download and ((self._state.adding and self.link) or \
        (not self._state.adding and self._old_link != self.link)):
            self.edited = now()

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

    def filename(self):
        return os.path.basename(self.download.name)

    def rendering_name(self):
        return os.path.basename(self.rendering.name)

    @property
    def file(self):
        if not hasattr(self, '_fileEx'):
            mime = MimeType(filename=self.download.path)
            self._fileEx = FileEx(self.download.file, mime)
        return self._fileEx

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

    def rendering_url(self):
        if self.rendering:
            return self.rendering.url
        if self.download and self.mime().is_image():
            return self.download.url
        if self.thumbnail and os.path.exists(self.thumbnail.path):
            return self.thumbnail.url
        return self.icon_url()

    def thumbnail_url(self):
        """Returns a 190px thumbnail either from the thumbnail,
           the image itself or the mimetype icon"""
        if self.thumbnail and os.path.exists(self.thumbnail.path):
            return self.thumbnail.url
        if self.rendering and os.path.exists(self.rendering.path):
            return self.rendering.url
        if self.download and self.mime().is_image() \
              and os.path.exists(self.download.path) \
              and self.download.size < settings.MAX_PREVIEW_SIZE:
                return self.download.url
        return self.icon_url()

    def icon_url(self):
        if not self.download:
            icon = "broken"
            if self.link:
                icon = "video" if self.is_video else "link"
            return self.mime().static(icon)
        return self.mime().icon()

    def as_lines(self):
        """Returns the contents as text"""
        return syntaxer(self.as_text(), self.mime())

    def as_line_preview(self):
        """Returns a few lines of text"""
        return syntaxer(self.as_text(20), self.mime())

    def as_text(self, lines=None):
        return self.file.as_text(lines=lines)

    @property
    def is_pasted(self):
        # Using pk is 1 is NOT idea, XXX find a better way.
        return self.category_id and self.category_id == 1

    def get_absolute_url(self):
        if self.is_pasted:
            return reverse('pasted_item', args=[str(self.pk)])
        if self.slug:
            return reverse('resource', kwargs={'username': self.user.username, 'slug': self.slug})
        return reverse('resource', kwargs={'pk': self.pk})

    @property
    def years(self):
        if self.created and self.edited \
          and self.created.year != self.edited.year:
            return "%d-%d" % (self.created.year, self.edited.year)
        if self.edited:
            return str(self.edited.year)
        if self.created is None:
            self.created = now()
            self.save()
        return str(self.created.year)

    # for counting detail views
    def set_viewed(self, session):
        if session.session_key is not None:
            # We check for session key because it might not exist if this
            # was called from the first view or cookies are blocked.
            (view, is_new) = self.views.get_or_create(session=session.session_key)
            return is_new
        return None

    def is_visible(self):
        return get_user().pk == self.user_id or self.published and self.is_available()

    def is_available(self):
        return not self.download or os.path.exists(self.download.path)

    def voted(self):
        return self.votes.filter(voter_id=get_user().pk).first()

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
        return Resource.objects.filter(category__isnull=True, user_id=self.user.pk)\
                    .exclude(pk=self.pk).latest('created')

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


class ResourceRevision(Model):
    """When a resource gets edited and the file is changed, the old file ends up here."""
    resource   = ForeignKey(Resource, related_name='revisions')
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
        kw = Resource.objects.filter(pk=resource.pk).values('download', 'signature')[0]
        if kw['download'] != resource.download.name:
            kw['resource'] = resource
            obj = cls(**kw)
            obj.save()
            return obj


class MirrorQuerySet(QuerySet):
    def select_mirror(self, update=None):
        """Selects the next best mirror randomly from the mirror pool"""
        qs = self.filter(chk_return=200)
        if update:
            qs = qs.filter(sync_time__gte=update)
        # Attempt to weight the mirrors (needs CS review)
        import random
        total = sum(mirror.capacity for mirror in qs)
        compare = random.uniform(0, total)
        upto = 0
        for mirror in qs:
            if upto + mirror.capacity > compare:
                return mirror
            upto += mirror.capacity
        return None

    def breadcrumb_name(self):
        return _("Download Mirrors")

    def get_absolute_url(self):
        return reverse('mirror')


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

    objects = MirrorQuerySet.as_manager()

    @property
    def host(self):
        return self.url.split('/')[2]

    def get_absolute_url(self):
        return reverse('mirror', kwargs={'slug': self.uuid})

    @staticmethod
    def resources():
        """List of all mirrored resources"""
        return Resource.objects.filter(mirror=True)      

    @property
    def parent(self):
        return ResourceMirror.objects.all()

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


class GalleryQuerySet(QuerySet):
    def for_user(self, user):
        return self.get_queryset().filter(Q(user=user.id) | Q(items__published=True)).distinct()

    def get_absolute_url(self):
        obj = self.parent
        if isinstance(obj, get_user_model()):
            return reverse('galleries', kwargs={'username': obj.username})
        elif isinstance(obj, Group):
            return reverse('galleries', kwargs={'team': obj.team.slug})
        return None

    def breadcrumb_name(self):
        return _("Galleries")

    @property
    def parent(self):
        return self._hints.get('instance', getattr(self, 'instance', None))


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
    user = ForeignKey(settings.AUTH_USER_MODEL, related_name='galleries', default=get_user)
    group = ForeignKey(Group, related_name='galleries', **null)
    category = ForeignKey(Category, related_name='galleries', **null)

    name = CharField(max_length=64)
    slug = SlugField(max_length=70)
    desc = TextField(_('Description'), validators=[MaxLengthValidator(50192)], **null)
    thumbnail = ResizedImageField(_('Thumbnail'), 190, 190, **upto('thumb'))
    status = CharField(max_length=1, db_index=True, choices=GALLERY_STATUSES, **null)

    items = ManyToManyField(Resource, related_name='galleries', blank=True)

    contest_submit = DateField(help_text=_('Start a contest in this gallery on this date (UTC).'), **null)
    contest_voting = DateField(help_text=_('Finish the submissions and start voting (UTC).'), **null)
    contest_count  = DateField(help_text=_('Voting is finished, but the votes are being counted.'), **null)
    contest_finish = DateField(help_text=_('Finish the contest, voting closed, winner announced (UTC).'), **null)

    _is_generic = lambda self, a, b: a and a <= now().date() < b
    is_contest    = property(lambda self: bool(self.contest_submit))
    is_pending    = property(lambda self: self.contest_submit and self.contest_submit > now().date())
    is_submitting = property(lambda self: self._is_generic(self.contest_submit, self.contest_voting))
    is_voting     = property(lambda self: self._is_generic(self.contest_voting, (self.contest_count or self.contest_finish)))
    is_counting   = property(lambda self: self._is_generic(self.contest_count, self.contest_finish))
    is_finished   = property(lambda self: self.contest_finish and self.contest_finish <= now().date())

    objects = GalleryQuerySet.as_manager()

    def __unicode__(self):
        if self.category:
            return self.name
        elif self.group:
            return _(u"%(gallery_name)s (for group %(group_name)s)") \
                  % {'gallery_name': self.name, 'group_name': unicode(self.group)}
        return  _(u"%(gallery_name)s (by %(user_name)s)") \
                  % {'gallery_name': self.name, 'user_name': unicode(self.user)}

    def __str__(self):
        return unicode(self).encode('utf8')

    def tag_cloud(self):
        """Returns a cloud collection"""
        return Tag.objects.filter(resources__galleries__id=self.pk).as_cloud('resources')

    @property
    def votes(self):
        """Returns a queryset of Votes for this category"""
        return Vote.objects.filter(resource__galleries=self.pk)

    def save(self, *args, **kwargs):
        set_slug(self)
        super(Gallery, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.category:
            return reverse('resources', kwargs={
                'category': self.category.slug,
                'galleries': self.slug,
              })
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
    def winners(self):
        """Return the resource with the most votes"""
        if self.is_contest and self.is_finished:
            if self.contest_count is None:
                item = self.items.latest('liked')
                item.extra_status = Resource.CONTEST_WINNER
                item.save()
                self.contest_count = self.contest_finish
            return self.items.filter(extra_status=Resource.CONTEST_WINNER)
        return None

    @property
    def value(self):
        return self.slug

    @property
    def parent(self):
        if self.category:
            return self.category
        return (self.group or self.user).galleries.all()

    def is_visible(self):
        return self.items.for_user(get_user()).count() or self.is_editable()

    def is_editable(self):
        user = get_user()
        return user and (not user.id is None) and (
            self.user == user or user.is_superuser \
              or (user.groups.count() and self.group in user.groups.all()))

    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        for item in self.items.all():
            if item.is_visible():
                return item.icon_url()
        return static('images', 'folder.svg')

    def __len__(self):
        return self.items.count()


class VoteManager(Manager):
    def items(self):
        f = dict( ('votes__'+a,b) for (a,b) in self.core_filters.items() )
        return Resource.objects.filter(published=True, **f)

    def refresh(self):
        if 'resource' in self.core_filters:
            resource = self.core_filters['resource']
            resource.liked = self.count()
            resource.save()
            return resource

class Vote(Model):
    """Vote for a resource in some way"""
    resource = ForeignKey(Resource, related_name='votes')
    voter    = ForeignKey(settings.AUTH_USER_MODEL, related_name='favorites')

    objects = VoteManager()


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
  ('icons', _("Gallery Icons")),
  ('rows', _("Gallery Rows")),
)

class GalleryPlugin(CMSPlugin):
    limit    = PositiveIntegerField(_('Number of items per page'))
    source   = ForeignKey(Gallery)
    display  = CharField(_("Display Style"), max_length=32, choices=DISPLAYS, **null)

    @property
    def render_template(self):
        if self.display not in ('icons', 'rows'):
            self.display = 'icons'
            self.save()
        return "resources/resource_%s.html" % self.display

class CategoryPlugin(CMSPlugin):
    limit    = PositiveIntegerField(_('Number of items per page'))
    source   = ForeignKey(Category)
    display  = CharField(_("Display Style"), max_length=32, choices=DISPLAYS, **null)

    @property
    def render_template(self):
        if self.display not in ('icons', 'rows'):
            self.display = 'icons'
            self.save()
        return "resources/resource_%s.html" % self.display

