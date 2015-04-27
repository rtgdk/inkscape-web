#
# A monkey patch module for auth.user, fixes many issues with django's default
# implimentation, but obviously might cause issues later so be careful with it.
#

from django.contrib.auth.models import User, Group
from django.db.models import Model
from django.utils import timezone
from types import FunctionType as function
from django.core import urlresolvers
from django.utils.encoding import smart_text, smart_bytes

def name(self):
    """Adds the first and last name as a full name or username"""
    if self.first_name or self.last_name:
        return self.get_full_name()
    return self.username

def __str__(self):
    return smart_bytes(self.name())

def __unicode__(self):
    return smart_text(self.name())

def get_absolute_url(self):
    return urlresolvers.reverse('view_profile', kwargs={'username':self.username})

def sessions(self):
    return self.session_set.filter(expire_date__gt=timezone.now())
  
def is_moderator(self):
    return self.has_perm("comments.can_moderate")

def visited_by(self, by_user):
    if by_user != self:
        self.details.visits += 1
        self.details.save()

local = locals().items()

for (key, d) in local:
    if type(d) is function:
        setattr(User, key, d)

