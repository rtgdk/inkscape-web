
import os
import inkscape.settings

from django.db.models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group

from .fields import AutoOneToOneField

class UserDetails(Model):
    user  = AutoOneToOneField(User, related_name='details')
    bio   = TextField(null=True, blank=True)
    photo = ImageField(_('Photograph'), null=True, blank=True,
              upload_to=os.path.join(settings.MEDIA_ROOT, 'photos'))

    def roll(self):
        if not self.user.is_active:
            return None
        for group in self.user.groups.all():
            if group.roll.name == 'Super User':
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
        return os.path.join(settings.MEDIA_URL, *self.photo.url.split('/')[-2:])


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

