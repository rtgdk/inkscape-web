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
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.text import slugify

# Thread-safe current user middleware getter.
from cms.utils.permissions import get_current_user as get_user

import fix_django

UserModel = get_user_model()
MODERATED = getattr(settings, 'MODERATED_MODELS', [])

# We're going to start with fixed flag types
FLAG_TYPES = (
    (1,   _('Removal Suggestion')),
    (5,   _('Moderator Approval')),
    (10,  _('Moderator Deletion')),
)

class TargetManager(Manager):
    def get_query_set(self):
        # This requires fix_django.
        return Manager.get_query_set(self).annotate(count=Count('target'), status=Max('flag')).order_by('-flagged')

    def recent(self):
        return self.get_query_set().filter(status=1)[:5]

    def get_status(self):
        return (self.get_query_set().values_list('status', flat=True) or [0])[0]

    def is_flagged(self):
        return self.get_status() == 1

    def is_approved(self):
        return self.get_status() == 5

    def is_deleted(self):
        return self.get_status() == 10

    def i_flagged(self):
        return self.exists(flagger=get_user())

    def exists(self, **kwargs):
        try:
            return bool(self.get(**kwargs))
        except self.model.DoesNotExist:
            return False

    def flag_url(self):
        obj = getattr(self, 'instance', None)
        if obj:
            return reverse('moderation.flag', kwargs=dict(pk=obj.pk, **self.model._url_keys()))
        return reverse('moderation.flagged', kwargs=dict(**self.model._url_keys()))

    def latest_url(self):
        return reverse('moderation.latest', kwargs=dict(**self.model._url_keys()))

    def flag(self, flag=1):
        return self.get_or_create(target=getattr(self, 'instance', None), flag=flag)


class FlagManager(Manager):
    def get_or_create(self, *args, **kwargs):
        if self.model is Flag:
            return get_flag_cls(**kwargs).objects.get_or_create(*args, **kwargs)
        return Manager.get_or_create(self, *args, **kwargs)


@python_2_unicode_compatible
class FlagCategory(Model):
    name = CharField(max_length=128)
    flag = IntegerField(_('Flag Type'), choices=FLAG_TYPES, default=1)

    def __str__(self):
        return self.name


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
    flagger    = ForeignKey(UserModel, verbose_name=_('Flagging User'), related_name="flagged", default=get_user)
    implicated = ForeignKey(UserModel, verbose_name=_('Implicated User'),
                                       related_name="flags_against", null=True, blank=True)
    category   = ForeignKey(FlagCategory, related_name="flags", null=True, blank=True)
    accusation = TextField(null=True, blank=True)
    flagged    = DateTimeField(_('Date Flagged'), default=now, db_index=True)
    flag       = IntegerField(_('Flag Type'), choices=FLAG_TYPES, default=1)
    target     = None

    class Meta:
        get_latest_by = 'flagged'

    def __str__(self):
        return "%s of %s by %s" % (self.flag, str(self.target), str(self.flagger))

    def _get_unique_checks(self, exclude=False):
        """Because of the cross-model relationship, we must add unique checks"""
        (a,b) = Flag._get_unique_checks(self, exclude=exclude)
        return [(type(self), ['target', 'flagger', 'flag'])], b

    @classmethod
    def _url_keys(cls):
        ct = ContentType.objects.get_for_model(cls.t_model)
        return dict(zip( ('app', 'name'), ct.natural_key()) )

    def hide_url(self):
        return reverse('moderation.hide', kwargs=dict(pk=self.pk, **self._url_keys()))

    def approve_url(self):
        return reverse('moderation.approve', kwargs=dict(pk=self.pk, **self._url_keys()))

    def save(self, *args, **kwargs):
        # Add owner object when specified by the target class
        if self.t_user == '-self':
            self.implicated = self.target
        elif self.t_user:
            self.implicated = getattr(self.target, self.t_user)
        return super(Flag, self).save(*args, **kwargs)


def template_ok(t):
    try:
        return loader.get_template(t) and t
    except Exception:
        return None

def get_flag_cls(target='', **kwargs):
    return globals().get(target+'Flag', Flag)

def get_user_for(klass):
    if klass is UserModel:
        return '-self'
    ret = []
    for field in klass._meta.fields:
        try:
            if field.rel.to is UserModel:
                ret.append(field)
        except AttributeError:
            pass
    if len(ret) > 1:
        raise AttributeError("More than one user field in moderated model, please specify which is the owner.")
    return ret and ret[0].name or None

def create_flag_model(klass):
    """Create a brand new Model for each Flag type, using Flag as a base class
       these are NOT upgradable (NO schema migrations)."""
    # Set up a dictionary to simulate declarations within a class
    attrs = {
      '__module__': __name__,
      't_model'   : klass,
      't_user'    : get_user_for(klass),
      'target'    : ForeignKey(klass, related_name='moderation', db_index=True),
      'template'  : template_ok('moderation/items/%s.html' % klass.__name__.lower()),
      'targets'   : TargetManager(),
      'objects'   : FlagManager(),
    }

    local_name = klass.__name__ + 'Flag'
    return (local_name, type(local_name, (Flag,), attrs))

class FlagSection(object):
    def __init__(self, label, cls):
        self.label   = label
        self.klass   = cls
        self.objects = cls.objects
        self.targets = cls.targets
        self.template = cls.template

    def __unicode__(self):
        return self.label

MODERATED_SELECTIONS = []
MODERATED_INDEX = {}
for (app_model, label) in MODERATED:
    ct = ContentType.objects.get_by_natural_key(*app_model.split('.'))
    (local_name, new_cls) = create_flag_model(ct.model_class())
    locals()[local_name] = new_cls
    MODERATED_SELECTIONS.append( FlagSection(label, new_cls) )

