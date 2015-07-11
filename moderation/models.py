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
from django.db.utils import OperationalError

from django.template import loader
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.text import slugify

# Thread-safe current user middleware getter.
from cms.utils.permissions import get_current_user as get_user

import fix_django

MODERATED = getattr(settings, 'MODERATED_MODELS', [])
MODERATED_SELECTIONS = []
MODERATED_INDEX = {}

# We're going to start with fixed flag types
FLAG_TYPES = (
    (1,   _('Removal Suggestion')),
    (5,   _('Moderator Approval')),
    (10,  _('Moderator Deletion')),
)

class TargetManager(Manager):
    def get_queryset(self):
        # This requires fix_django.
        return Manager.get_queryset(self).annotate(count=Count('target'), status=Max('flag')).order_by('-flagged')

    def recent(self):
        return self.get_queryset().filter(status=1)[:5]

    def get_status(self):
        return (self.get_queryset().values_list('status', flat=True) or [0])[0]

    def is_flagged(self):
        return self.get_status() == 1

    def is_approved(self):
        return self.get_status() == 5

    def is_deleted(self):
        return self.get_status() == 10

    def i_flagged(self):
        user = get_user()
        if user.is_authenticated():
            return self.exists(flagger=user.pk)
        return False

    def exists(self, **kwargs):
        try:
            return bool(self.get(**kwargs))
        except self.model.DoesNotExist:
            return False

    def flag_url(self):
        obj = getattr(self, 'instance', None)
        if obj:
            return self.model.get_url('moderation.flag', pk=obj.pk)
        return self.model.get_url('moderation.flagged')

    def latest_url(self):
        return self.model.get_url('moderation.latest')

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
    flagger    = ForeignKey(settings.AUTH_USER_MODEL, default=get_user,
                     verbose_name=_('Flagging User'), related_name="flagged")
    implicated = ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Implicated User'),
                           related_name="flags_against", null=True, blank=True)
    category   = ForeignKey(FlagCategory, related_name="flags", null=True, blank=True)
    accusation = TextField(validators=[MaxLengthValidator(1024)], null=True, blank=True)
    flagged    = DateTimeField(_('Date Flagged'), default=now, db_index=True)
    flag       = IntegerField(_('Flag Type'), choices=FLAG_TYPES, default=1)
    target     = None

    class Meta:
        get_latest_by = 'flagged'

    @classmethod
    def target_ct(cls):
        return ContentType.objects.get_by_natural_key(*cls.t_model.split('.'))

    @classmethod
    def get_url(cls, name, **kwargs):
        kw = dict(zip(('app', 'name'), cls.target_ct().natural_key()))
        kw.update(kwargs)
        return reverse(name, kwargs=kw)

    def __str__(self):
        return "%s of %s by %s" % (self.flag, str(self.target), str(self.flagger))

    def _get_unique_checks(self, exclude=False):
        """Because of the cross-model relationship, we must add unique checks"""
        (a,b) = Flag._get_unique_checks(self, exclude=exclude)
        return [(type(self), ['target', 'flagger', 'flag'])], b

    def hide_url(self):
        return self.get_url('moderation.hide', pk=self.pk)

    def approve_url(self):
        return self.get_url('moderation.approve', pk=self.pk)

    @property
    def target_user(self):
        klass = get_model(*self.target_ct().natural_key())
        auth_klass = get_model(*settings.AUTH_USER_MODEL.split('.',1))
        if klass is auth_klass:
            return '-self'
        ret = []
        for field in klass._meta.fields:
            try:
                if field.rel.to is auth_klass:
                    ret.append(field)
            except AttributeError:
                pass
        if len(ret) > 1:
            raise AttributeError("More than one user field in moderated model, please specify which is the owner.")
        return ret and ret[0].name or None

    def save(self, *args, **kwargs):
        # Add owner object when specified by the target class
        if self.target_user == '-self':
            self.implicated = self.target
        elif self.target_user:
            self.implicated = getattr(self.target, self.target_user)
        return super(Flag, self).save(*args, **kwargs)


def template_ok(t):
    try:
        return loader.get_template(t) and t
    except Exception:
        return None

def get_flag_cls(target='', **kwargs):
    return globals().get(target+'Flag', Flag)

def create_flag_model(klass):
    """Create a brand new Model for each Flag type, using Flag as a base class
       these are NOT upgradable (NO schema migrations)."""
    # Set up a dictionary to simulate declarations within a class
    name = klass.split('.')[-1]
    attrs = {
      '__module__': __name__,
      't_model'   : klass,
      'target'    : ForeignKey(klass, related_name='moderation', db_index=True),
      'template'  : template_ok('moderation/items/%s.html' % name.lower()),
      'targets'   : TargetManager(),
      'objects'   : FlagManager(),
    }

    local_name = name.title() + 'Flag'
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

for (app_model, label) in MODERATED:
    (local_name, new_cls) = create_flag_model(app_model)
    locals()[local_name] = new_cls
    MODERATED_SELECTIONS.append( FlagSection(label, new_cls) )

