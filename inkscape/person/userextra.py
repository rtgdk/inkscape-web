#
# A monkey patch module for auth.user, fixes many issues with django's default
# implimentation, but obviously might cause issues later so be careful with it.
#

def name(self):
    """Adds the first and last name as a full name or username"""
    if self.first_name or self.last_name:
        return self.get_full_name()
    return self.username

def __str__(self):
        return self.name

def get_url(self):
    return reverse('view_profile', args=[str(self.id)])

def sessions(self):
    from django.utils.timezone import now
    return self.session_set.filter(expire_date__gt=now())

local = locals().items()
from django.contrib.auth.models import User, Group

for (key, d) in local:
    setattr(User, key, d)

