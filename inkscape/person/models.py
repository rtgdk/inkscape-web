
import os
import inkscape.settings

from django.db.models import *
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator

from pile.fields import ResizedImageField, AutoOneToOneField

null = dict(null=True, blank=True)

from .userextra import User, Group

class UserDetails(Model):
    user  = AutoOneToOneField(User, related_name='details')
    bio   = TextField(validators=[MaxLengthValidator(4096)], **null)
    photo = ResizedImageField(_('Photograph'), null=True, blank=True,
              upload_to='photos', max_width=190, max_height=190)

    ircnick = CharField(_('IRC Nickname'), max_length=20, **null)
    ircpass = CharField(_('Freenode Password (optional)'), max_length=128, **null)
    ircdev  = BooleanField(_('Join Developer Channel'), default=False)

    dauser  = CharField(_('deviantArt User'), max_length=64, **null)
    ocuser  = CharField(_('openClipArt User'), max_length=64, **null)
    tbruser = CharField(_('Tumblr User'), max_length=64, **null)
    gpg_key = TextField(_('GPG Public Key'), validators=[MaxLengthValidator(262144)], **null)

    last_seen = DateTimeField(**null)
    visits    = IntegerField(default=0)

    def __unicode__(self):
        if self.user.first_name:
            return "%s %s" % (self.user.first_name, self.user.last_name)
        return self.user.username

    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None


ENROLES = (
  ('O', _('Open')),
  ('P', _('Peer Invite')),
  ('T', _('Admin Invite')),
  ('C', _('Closed')),
)

class Team(Model):
    worker = ForeignKey(Group, related_name='teams', **null)
    admin  = ForeignKey(Group, related_name='admin_teams', **null)

    name  = CharField(_('User Team'), max_length=32)
    icon  = ImageField(_('Display Icon'), upload_to='teams')

    intro = TextField(_('Introduction'), validators=[MaxLengthValidator(1024)], **null)
    desc  = TextField(_('Full Description'), validators=[MaxLengthValidator(10240)], **null)

    mailman = CharField(_('Mailing List'), max_length=256, **null)
    enrole  = CharField(_('Open Enrolement'), max_length=1, default='O', choices=ENROLES)

    def __unicode__(self):
        return self.name

class TeamMembership(Model):
    team = ForeignKey(Team, related_name='members')
    user = ForeignKey(User, related_name='teams')

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


