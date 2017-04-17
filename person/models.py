#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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

import os

from django.conf import settings
from django.db.models import *
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from django.utils import timezone
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _, get_language
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator
from django.contrib.sessions.models import Session

from django.contrib.auth.models import Group, AbstractUser
from pile.fields import ResizedImageField, AutoOneToOneField

null = dict(null=True, blank=True)

@python_2_unicode_compatible
class User(AbstractUser):
    bio   = TextField(_('Bio'), validators=[MaxLengthValidator(4096)], **null)
    photo = ResizedImageField(_('Photograph (square)'), null=True, blank=True,
              upload_to='photos', max_width=190, max_height=190)
    language = CharField(_('Default Language'), max_length=8, choices=settings.LANGUAGES, **null)

    ircnick = CharField(_('IRC Nickname'), max_length=20, **null)
    ircpass = CharField(_('Freenode Password (optional)'), max_length=128, **null)

    dauser  = CharField(_('deviantArt User'), max_length=64, **null)
    ocuser  = CharField(_('Openclipart User'), max_length=64, **null)
    tbruser = CharField(_('Tumblr User'), max_length=64, **null)
    gpg_key = TextField(_('GPG Public Key'),
        help_text=_('<strong>Signing and Checksums for Uploads</strong><br/> '
                    'Either fill in a valid GPG key, so you can sign your uploads, '
                    'or just enter any text to activate the upload validation feature '
                    'which verifies your uploads by comparing checksums.<br/>'
                    '<strong>Usage in file upload/editing form:</strong><br/>'
                    'If you have submitted a GPG key, you can upload a *.sig file, '
                    'and your upload can be verified. You can also submit these checksum file types:<br/>'
                    '*.md5, *.sha1, *.sha224, *.sha256, *.sha384 or *.sha512'),
        validators=[MaxLengthValidator(262144)], **null)

    last_seen = DateTimeField(**null)
    visits    = IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self.first_name or self.last_name:
            return self.get_full_name()
        return self.username

    class Meta:
        permissions = [
            ("use_irc", _("IRC Chat Training Complete")),
            ("website_cla_agreed", _("Agree to Website License")),
        ]
        db_table = 'auth_user'

    def get_ircnick(self):
        if not self.ircnick:
            return self.username
        return self.ircnick

    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None

    def photo_preview(self):
        if self.photo:
            return '<img src="%s" style="max-width: 200px; max-height: 250px;"/>' % self.photo.url
        # Return an embedded svg, it's easier than dealing with static files.
        return """
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="200" height="250">
           <path style="stroke:#6c6c6c;stroke-width:.5px;fill:#ece8e6;"
           d="m1.2 1.2v248h27.6c-9.1-43 8-102 40.9-123-49.5-101 111-99.9 61.5 1.18 36.6 35.4 48.6 78.1 39.1 122h28.5v-248z"
           /></svg>"""
    photo_preview.allow_tags = True

    def quota(self):
        from resources.models import Quota
        groups = Q(group__in=self.groups.all()) | Q(group__isnull=True)
        quotas = Quota.objects.filter(groups)
        if quotas.count():
            return quotas.aggregate(Max('size'))['size__max'] * 1024
        return 0

    def get_absolute_url(self):
        if not self.username:
            return '/'
        return reverse('view_profile', kwargs={'username':self.username})

    def is_moderator(self):
        return self.has_perm("moderation.can_moderate")

    def visited_by(self, by_user):
        if by_user != self:
            self.visits += 1
            self.save(update_fields=['visits'])

    @property
    def teams(self):
        return Team.objects.filter(group__in=self.groups.all())

    def viewer_is_subscribed(self):
        from cms.utils.permissions import get_current_user as get_user
        user = get_user()
        if user.is_authenticated():
	    return bool(self.resources.subscriptions().get(user=user.pk))
        return False


@receiver(post_save, sender=User)
def is_active_check(sender, instance, **kwargs):
    """Delete every session when active is False"""
    from django.contrib.auth import SESSION_KEY
    if not instance.is_active:
        for session in Session.objects.all():
            # There is google-oauth sessions which aren't cleared here
            try:
                if int(session.get_decoded().get(SESSION_KEY), -1) == instance.pk:
                    session.delete()
            except Exception:
                pass



def group_breadcrumb_name(self):
    try:
        return str(self.team)
    except:
        return str(self)
Group.breadcrumb_name = group_breadcrumb_name


class TwilightSparkle(Manager):
    def i_added(self):
        from cms.utils.permissions import get_current_user as get_user
        user = get_user()
        if user.is_authenticated():
            return bool(self.get(from_user=user.pk))
        return False

    def mutual(self):
        """Returns a mutual set of friends"""
        return self.get_queryset()\
                .filter(from_user__from_friends__from_user=F('user'))

@python_2_unicode_compatible
class Friendship(Model):
    from_user = ForeignKey(User, related_name='friends')
    user      = ForeignKey(User, related_name='from_friends')

    objects   = TwilightSparkle()

    def __str__(self):
        return u"%s loves %s" % (str(self.from_user), str(self.user))

@python_2_unicode_compatible
class TeamChatRoom(Model):
    admin    = ForeignKey(User, **null)
    channel  = CharField(_('IRC Chatroom Name'), max_length=64)
    language = CharField(max_length=5, default='en', choices=settings.LANGUAGES)
    team     = ForeignKey('Team', related_name='ircrooms')

    class Meta:
        unique_together = (('language', 'team'),)

    def __str__(self):
        return 'IRC: %s' % self.channel


class TeamQuerySet(QuerySet):
    def breadcrumb_name(self):
        return _('Inkscape Community Teams')

    def get_absolute_url(self):
        return reverse('teams')


class Team(Model):
    ENROLES = (
      ('O', _('Open')),
      ('P', _('Peer Approval')),
      ('T', _('Admin Approval')),
      ('C', _('Closed')),
      ('S', _('Secret')),
    )
    ICON = os.path.join(settings.STATIC_URL, 'images', 'team.svg')

    admin = ForeignKey(User, related_name='admin_teams', **null)
    group = AutoOneToOneField(Group, related_name='team')
    watchers = ManyToManyField(User, related_name='watches', blank=True)
    requests = ManyToManyField(User, related_name='team_requests', blank=True)

    name = CharField(_('Team Name'), max_length=32)
    slug = SlugField(_('Team URL Slug'), max_length=32)
    icon = ImageField(_('Display Icon'), upload_to='teams', default=ICON)

    intro = TextField(_('Introduction'), validators=[MaxLengthValidator(1024)], **null)
    desc = TextField(_('Full Description'), validators=[MaxLengthValidator(10240)], **null)
    charter = TextField(_('Charter'), validators=[MaxLengthValidator(30240)], **null)
    side_bar = TextField(_('Side Bar'), validators=[MaxLengthValidator(10240)], **null)

    mailman = CharField(_('Email List'), max_length=32, null=True, blank=True,
        help_text='The name of the pre-configured mailing list for this team')
    enrole = CharField(_('Enrollment'), max_length=1, default='O', choices=ENROLES)

    localized_fields = ('name', 'intro', 'desc',  'charter', 'side_bar')
    objects = TeamQuerySet.as_manager()

    @property
    def channels(self):
        return self.ircrooms.filter(language__in=[get_language(), 'en'])\
                .values('language', 'channel')

    @property
    def members(self):
        return self.group.user_set

    @property
    def parent(self):
        return type(self).objects.all()

    @property
    def team(self):
        return self

    @property
    def peers(self):
        if self.enrole == 'P':
            return list(self.members.all()) + [self.admin]
        return [self.admin]

    def get_absolute_url(self):
        return reverse('team', kwargs={'team': self.slug})

    def save(self, **kwargs):
        if not self.name:
            self.name = self.group.name
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Team, self).save(**kwargs)

    def __unicode__(self):
        return self.name


def subscribe_to_list(action, team, user):
    pass # Re-enable when we are using mailman3
#    if action == 'pre_remove':
#        team.mailman.unsubscribe(user.email)
#    elif action == 'post_add':
#        team.mailman.subscribe(user.email, user.first_name, user.last_name)

def update_mailinglist(model, pk_set, instance, action, **kwargs):
    """Subscribe member to mailing list if needed"""
    pass
#    if not hasattr(instance, 'team'):
#        return
#    team = instance.team
#    team.mailman_users = []
#    if not pk_set or not pk_set | {None}:
#        return
#    for user in model.objects.filter(pk__in=pk_set):
#        if user.email and team.mailman:
#            try:
#                subscribe_to_list(action, team, user)
#            except Exception:
#                team.mailman_users.append(user.pk)
#            finally:
#                team.mailman_users.append(user)

def exclusive_subscription(model, pk_set, instance, action, reverse=False, **kwargs):
    if action == 'post_add' and reverse:
        instance.team.watchers.remove(*list(pk_set))

def exclusive_watching(model, pk_set, instance, action, reverse=False, **kwargs):
    if action == 'post_add' and reverse:
        instance.team.group.user_set.remove(*list(pk_set))

m2m_changed.connect(update_mailinglist, sender=Team.watchers.through)
m2m_changed.connect(update_mailinglist, sender=User.groups.through)
m2m_changed.connect(exclusive_watching, sender=Team.watchers.through)
m2m_changed.connect(exclusive_subscription, sender=User.groups.through)

# Patch in the url so we get a better front end view from the admin.
def get_team_url(self):
    try:
        return self.team.get_absolute_url()
    except Team.DoesNotExist:
        return '/'
Group.get_absolute_url = get_team_url

