#
# A monkey patch module for auth.user, fixes many issues with django's default
# implimentation, but obviously might cause issues later so be careful with it.
#

from django.contrib.auth.models import User, Group
from django.db.models import Model
from django.utils import timezone
from types import FunctionType as function

def name(self):
    """Adds the first and last name as a full name or username"""
    if self.first_name or self.last_name:
        return self.get_full_name()
    return self.username

def __str__(self):
        return self.name()

def get_url(self):
    return reverse('view_profile', args=[str(self.id)])

def sessions(self):
    return self.session_set.filter(expire_date__gt=timezone.now())

local = locals().items()

for (key, d) in local:
    if type(d) is function:
        setattr(User, key, d)

