
import os
import inkscape.settings

from django.db.models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

from inkscape.fields import ResizedImageField, AutoOneToOneField

null = dict(null=True, blank=True)


def forced_insert(self):
    """Adds the first and last name as a full name or username"""
    if self.first_name or self.last_name:
        return self.get_full_name()
    return self.username

def get_url(self):
    return reverse('view_profile', args=[str(self.id)])

User.name = forced_insert
User.__str__ = forced_insert
User.get_absolute_url = get_url

class UserDetails(Model):
    user  = AutoOneToOneField(User, related_name='details')
    bio   = TextField(**null)
    photo = ResizedImageField(_('Photograph'), null=True, blank=True,
              upload_to=os.path.join('photos'), max_width=190, max_height=190)

    ircnick = CharField("IRC Nickname", max_length=20, **null)
    ircpass = CharField("Freenode Password (optional)", max_length=128, **null)
    ircdev  = BooleanField("Join Developer Channel", default=False)

    dauser  = CharField("deviantArt User", max_length=64, **null)
    ocuser  = CharField("openClipArt User", max_length=64, **null)
    tbruser = CharField("Tumblr User", max_length=64, **null)

    last_seen = DateTimeField(**null)
    visits    = IntegerField(default=0)

    def roll(self):
        if not self.user.is_active:
            return None
        for group in self.user.groups.all():
            if group.roll.name == 'Administrator':
                if self.user.is_superuser:
                    return group.roll
            elif group.roll:
                return group.roll
        return UserRoll.objects.all()[0]

    def __unicode__(self):
        if self.user.first_name:
            return "%s %s" % (self.user.first_name, self.user.last_name)
        return self.user.username

    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None


class UserRoll(Model):
    group = OneToOneField(Group, related_name='roll')
    name  = CharField("User Roll", max_length=32)
    desc  = TextField(null=True, blank=True)
    icon  = ImageField(_('Display Icon'),
        upload_to=os.path.join(settings.MEDIA_ROOT, 'rollicons'))

    def __unicode__(self):
        return self.name

    def icon_url(self):
        return os.path.join(settings.MEDIA_URL, *self.icon.url.split('/')[-2:])

