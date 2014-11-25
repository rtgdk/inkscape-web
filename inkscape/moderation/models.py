#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Moderation is achieved using a generic flagging model and some further
 User monitoring which should allow users to manage each other in a
 healthy community atmosphere.
"""

#
# Note about implementation: We would have used GenericForeignKey
#  but the support for back references and aggregations in django 1.6.5
#  was so bad that it just didn't work.
#

from django.db.models import *

from django.template import loader
from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.text import slugify

import fix_django

MODERATED = getattr(settings, 'MODERATED_MODELS', [])

# We're going to start with fixed flag types
FLAG_TYPES = (
    ('flag',    _('Removal Suggestion')),
    ('delete',  _('Moderator Deletion')),
    ('approve', _('Moderator Approval')),
)

class TargetManager(Manager):
    def get_query_set(self):
        # This requires fix_django.
        return Manager.get_query_set(self).annotate(count=Count('target')).order_by('-flagged')

    def recent(self):
        return self.get_query_set()[:5]


class FlagManager(Manager):
    def get_or_create(self, *args, **kwargs):
        if self.model is Flag:
            return get_flag_cls(**kwargs).objects.get_or_create(*args, **kwargs)
        return Manager.get_or_create(self, *args, **kwargs)


@python_2_unicode_compatible
class Flag(Model):
    """
    Records a flag on any object. A flag could be:

        * A "removal suggestion" -- where a user suggests a comment for (potential) removal.
        * A "moderator deletion" -- used when a moderator deletes a comment.

    You can (ab)use this model to add other flags, if needed. However, by
    design users are only allowed to flag a comment with a given flag once;
    if you want rating look elsewhere.
    """
    user     = ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Flagging User'), related_name="flagged")
    flag     = CharField(_('Flag Type'), max_length=16, choices=FLAG_TYPES, db_index=True)
    flagged  = DateTimeField(_('Date Flagged'), default=now, db_index=True)
    target   = None

    class Meta:
        get_latest_by = 'flagged'

    def __str__(self):
        return "%s of %s by %s" % (self.flag, str(self.target), str(self.user))


def template_ok(t):
    try:
        return loader.get_template(t) and t
    except Exception:
        return None

def get_flag_cls(target='', **kwargs):
    return globals().get(target+'Flag', Flag)

def create_flag_model(klass):
    class Meta:
        unique_together = [('target')]
    def _get_unique_checks(self, exclude=False):
        """Because of the cross-model relationship, we must add unique checks"""
        (a,b) = Flag._get_unique_checks(self, exclude=exclude)
        return [(type(self), ['target', 'user', 'flag'])], b

    # Set up a dictionary to simulate declarations within a class
    attrs = {
      '__module__': __name__,
      'Meta'      : Meta,
      't_model'   : klass,
      'target'    : ForeignKey(klass, related_name='flags', db_index=True),
      '_get_unique_checks': _get_unique_checks,
      'template'  : template_ok('moderation/items/%s.html' % klass.__name__.lower()),
      'targets'   : TargetManager(),
      'objects'   : FlagManager(),
    }

    local_name = klass.__name__ + 'Flag'
    return (local_name, type(local_name, (Flag,), attrs))

#
# We create a new model per moderated class, these are NOT upgradable (NO schema migrations).
#
class FlagCategory(object):
    def __init__(self, label, cls):
        self.label   = label
        self.klass   = cls
        self.objects = cls.objects
        self.targets = cls.targets

    def __unicode__(self):
        return self.label

MODERATED_CATEGORIES = []
for (app_model, label) in MODERATED:
    ct = ContentType.objects.get_by_natural_key(*app_model.split('.'))
    (local_name, new_cls) = create_flag_model(ct.model_class())
    locals()[local_name] = new_cls
    MODERATED_CATEGORIES.append( FlagCategory(label, new_cls) )

