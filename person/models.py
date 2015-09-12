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
from django.db.models.signals import m2m_changed
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator
from django.utils.text import slugify

from pile.fields import ResizedImageField, AutoOneToOneField

null = dict(null=True, blank=True)

from .userextra import User, Group

class UserDetails(Model):
    user  = AutoOneToOneField(User, related_name='details')
    bio   = TextField(validators=[MaxLengthValidator(4096)], **null)
    photo = ResizedImageField(_('Photograph (square)'), null=True, blank=True,
              upload_to='photos', max_width=190, max_height=190)
    language = CharField(_('Default Language'), max_length=8, choices=settings.LANGUAGES, **null)

    ircnick = CharField(_('IRC Nickname'), max_length=20, **null)
    ircpass = CharField(_('Freenode Password (optional)'), max_length=128, **null)
    ircdev  = BooleanField(_('Join Developer Channel'), default=False)

    dauser  = CharField(_('deviantArt User'), max_length=64, **null)
    ocuser  = CharField(_('openClipArt User'), max_length=64, **null)
    tbruser = CharField(_('Tumblr User'), max_length=64, **null)
    gpg_key = TextField(_('GPG Public Key'), validators=[MaxLengthValidator(262144)], **null)

    last_seen = DateTimeField(**null)
    visits    = IntegerField(default=0)

    class Meta:
        permissions = [("website_cla_agreed", "Agree to Website License")]

    def __unicode__(self):
        if self.user.first_name:
            return "%s %s" % (self.user.first_name, self.user.last_name)
        return self.user.username

    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None


class TwilightSparkle(Manager):
    def i_added(self):
        from cms.utils.permissions import get_current_user as get_user
        user = get_user()
        if user.is_authenticated():
            return bool(self.get(from_user=user.pk))
        return False

class Friendship(Model):
    from_user = ForeignKey(User, related_name='friends')
    user      = ForeignKey(User, related_name='from_friends')

    objects   = TwilightSparkle()


class Team(Model):
    ENROLES = (
      ('O', _('Open')),
      ('P', _('Peer Approval')),
      ('T', _('Admin Approval')),
      ('C', _('Closed')),
      ('S', _('Secret')),
    )
    ICON = os.path.join(settings.STATIC_URL, 'images', 'team.svg')

    admin    = ForeignKey(User, related_name='admin_teams', **null)
    group    = AutoOneToOneField(Group, related_name='team')
    watchers = ManyToManyField(User, related_name='watches', **null)
    requests = ManyToManyField(User, related_name='team_requests', **null)

    name     = CharField(_('Team Name'), max_length=32)
    slug     = SlugField(_('Team URL Slug'), max_length=32)
    icon     = ImageField(_('Display Icon'), upload_to='teams', default=ICON)

    intro    = TextField(_('Introduction'), validators=[MaxLengthValidator(1024)], **null)
    desc     = TextField(_('Full Description'), validators=[MaxLengthValidator(10240)], **null)

    mailman  = ForeignKey('django_mailman.List', **null)
    enrole   = CharField(_('Enrolement'), max_length=1, default='O', choices=ENROLES)
    
    @property
    def members(self):
        return self.group.user_set

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

def _sub_ml(action, team, user):
    if action == 'pre_remove':
        team.mailman.unsubscribe(user.email)
    elif action == 'post_add':
        team.mailman.subscribe(user.email, user.first_name, user.last_name)

def update_mailinglist(model, pk_set, instance, action, **kwargs):
    """Subscribe member to mailing list if needed"""
    team = instance.team
    team.mailman_users = []
    for user in model.objects.filter(pk__in=pk_set):
        if user.email and team.mailman:
            try:
                _sub_ml(action, team, user)
            except Exception:
                team.mailman_users.append(user.pk)
            finally:
                team.mailman_users.append(user)


m2m_changed.connect(update_mailinglist, sender=Team.watchers.through)
m2m_changed.connect(update_mailinglist, sender=User.groups.through)

# Patch in the url so we get a better front end view from the admin.
Group.get_absolute_url = lambda self: self.team.get_absolute_url()
# Patch in a reverse lookup for teams so we get a solid team object list
User.teams = property(lambda self: Team.objects.filter(group__in=self.groups.all()))

class Ballot(Model):
    name  = CharField(max_length=128)
    team  = ForeignKey(Team, related_name='ballots')
    desc  = TextField(_('Full Description'), validators=[MaxLengthValidator(10240)], **null)

    def __str__(self):
        return self.name


class BallotItem(Model):
    ballot = ForeignKey(Ballot, related_name='items')
    name  = CharField(max_length=128)

    def __str__(self):
        return self.name


class BallotVotes(Model):
    ballot = ForeignKey(Ballot, related_name='votes')
    user   = ForeignKey(User, related_name='ballot_votes')
    item   = ForeignKey(BallotItem, related_name='votes')
    order  = IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'item', 'order')

    def __str__(self):
        return "%s's Vote on Ballot %s" % (self.user, self.ballot)


# ===== CMS Plugins ===== #


from cms.models import CMSPlugin

class GroupPhotoPlugin(CMSPlugin):
    STYLES = (
      ('L', _('Simple List')),
      ('P', _('Photo Heads')),
      ('B', _('Photo Bios')),
    )

    source = ForeignKey(Group)
    style  = CharField(_('Display Style'), max_length=1, choices=STYLES)


