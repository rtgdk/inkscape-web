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

from django.db.models import *
from django.db.models.signals import post_init

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator

from collections import defaultdict

null = {'null': True, 'blank': True}

class AlertTypeManager(Manager):
    def get_or_create(self, values=None, **kwargs):
        """Allow the AlertType to be updated with code values
           (should only be run on new code load or server restart)"""
        if values and 'defaults' not in kwargs:
            kwargs['defaults'] = values
        (obj, created) = super(AlertTypeManager, self).get_or_create(**kwargs)
        if not created and values:
            self.filter(pk=obj.pk).update(**values)
        return (obj, created)


class AlertType(Model):
    """All Possible messages that users can receive, acts as a template"""
    CATEGORIES = (
      ('?', 'Unknown'),
      ('U', 'User to User'),
      ('S', 'System to User'),
      ('A', 'Admin to User'),
      ('P', 'User to Admin'),
      ('T', 'System to Translator'),
    )

    slug     = CharField(_("URL Slug"),         max_length=32)
    group    = ForeignKey(Group, verbose_name=_("Limit to Group"), **null)

    created  = DateTimeField(_("Created Date"), auto_now_add=now)
    
    category = CharField(_("Category"), max_length=1, choices=CATEGORIES, default='?')
    enabled  = BooleanField(default=False)
    private  = BooleanField(default=False)

    # These get copied into UserAlertSettings for this alert
    default_hide  = BooleanField(default=False)
    default_email = BooleanField(default=False)

    objects = AlertTypeManager()

    def __init__(self, *args, **kwargs):
        super(AlertType, self).__init__(*args, **kwargs)
        # Late import to stop loop import
        from alerts.base import ALL_ALERTS
        self._alerter = ALL_ALERTS[self.slug]

    def __getattr__(self, name):
        if hasattr(self._alerter, name):
            return getattr(self._alerter, name)
        raise AttributeError("Can't find alert attribute: %s.%s" % (type(self).__name__, name))

    def send_to(self, user, auth=None, **kwargs):
        """Creates a new alert for a certain user of this type.

         user   - The user this alert should be addressed to. (required)
                  can also be a group, where upon each member of the group
                  will be messaged (be careful with this).
         auth   - Super user to authorise the sending of an alert to everyone
         kwargs - Dictionary of objects used in the rendering of the subject
                  and body templates.

         Returns new UserAlert object or None if user isn't allowed this alert.

        """
        if not self.enabled:
            return []
        if isinstance(user, Group):
            users = user.users
        elif isinstance(user, User):
            users = [ user ]
        elif user == 'all':
            if not isinstance(auth, User) or not auth.is_superuser:
                raise ValueError("You are not authorized to send an alert to everyone.")
            users = User.objects.all()
        else:
            raise ValueError("You must specify a user or group to send an alert to.")

        return [ self._send_to(real_user, **kwargs) for real_user in users ]

    def _send_to(self, user, **kwargs):
        if self.enabled and (not self.group or self.group in user.groups):
            if 'instance' in kwargs:
                # Check if the instance has already been issued to this user's alerts.
                i = kwargs['instance']
                existing = UserAlert.objects.filter(user=user, alert=self,
                    objs__o_id=i.pk, objs__name='instance').count()
                if existing:
                    return None
            alert = UserAlert(user=user, alert=self)
            alert.save()
            for (key, value) in kwargs.items() or ():
                if isinstance(value, Model):
                    UserAlertObject(alert=alert, name=key, target=value).save()
                else:
                    UserAlertValue(alert=alert, name=key, target=unicode(value)).save()
            return alert
        return None

    def __str__(self):
        return unicode(self.name)

for (m, name) in AlertType.CATEGORIES:
    name = 'CATEGORY_'+name.replace(' ', '_').upper()
    setattr(AlertType, name, m)


class SettingsManager(Manager):
    def get(self, **kwargs):
        """Will return an empty setting for this user using defaults"""
        try:
            return Manager.get(self, **kwargs)
        except self.model.DoesNotExist:
            if 'alert' in kwargs and 'user' in kwargs and len(kwargs) == 2:
                kwargs['hide'] = kwargs['alert'].default_hide
                kwargs['email'] = kwargs['alert'].default_email
                return self.model(**kwargs)
            raise

    def get_all(self, user):
        ret = []
        for alert_type in AlertType.objects.filter(enabled=True):
            ret.append(self.get(user=user, alert=alert_type))
        return ret


class UserAlertSetting(Model):
    user    = ForeignKey(User, related_name='alert_settings')
    alert   = ForeignKey(AlertType, related_name='settings')
    hide    = BooleanField(_("Hide Alerts"), default=True)
    email   = BooleanField(_("Send Email Alert"), default=False)
    
    objects = SettingsManager()

    def __str__(self):
        return "User Alert Setting"


class UserAlertManager(Manager):
    def __init__(self, target=None, alert_type=None):
        self.target = target
        self.alert_type = alert_type
        super(UserAlertManager, self).__init__()

    def __str__(self):
        return "UserAlertManager for '%s' (%s)" % \
            (str(self.target), type(self.target).__name__)

    def get_queryset(self):
        queryset = super(UserAlertManager, self).get_queryset()

        if self.target is not None:
            ct = UserAlertObject.target.get_content_type(obj=self.target)
            queryset = queryset.filter(objs__table=ct, objs__o_id=self.target.pk)

        if self.alert_type is not None:
            queryset = queryset.filter(alert=self.alert_type)

        return queryset.filter(deleted__isnull=True).order_by('-created')

    def new(self):
        return self.get_queryset().filter(viewed__isnull=True)

    def types(self):
        counts = defaultdict(int)
        # We'd use count and distinct to do this login in the db, but flakey
        for (slug, count) in self.new().values('alert')\
          .annotate(count=Count('alert')).values_list('alert__slug', 'count')\
          .order_by('alert__created'):
            counts[slug] += count
        for slug in counts.keys():
            yield (slug, SIGNALS[slug], counts[slug])

    def mark_viewed(self):
        return self.get_queryset().filter(viewed__isnull=True).update(viewed=now())


class UserAlert(Model):
    """A single altert for a specific user"""
    user    = ForeignKey(User, related_name='alerts')
    alert   = ForeignKey(AlertType, related_name='sent')

    created = DateTimeField(auto_now_add=True)
    viewed  = DateTimeField(**null)
    deleted = DateTimeField(**null)

    objects = UserAlertManager()

    subject = property(lambda self: self.alert.get_subject(self.data))
    body    = property(lambda self: self.alert.get_body(self.data))

    def view(self):
        if not self.viewed:
            self.viewed = now()
            self.save()

    def delete(self):
        if not self.deleted:
            self.deleted = now()
            self.save()

    def is_hidden(self):
        return self.viewed or self.deleted or self.config.hide

    @property
    def config(self):
        # This should auto-create but not save.
        return UserAlertSetting.objects.get(user=self.user, alert=self.alert)

    def __str__(self):
        return self.subject.strip() or "No Subject"

    @property
    def data(self):
        ret = self.objs.as_dict()
        ret.update(self.values.as_dict())
        return ret

    def save(self, **kwargs):
        create = not bool(self.created)
        ret = Model.save(self, **kwargs)
        # This means: We didn't exist, and now we do.
        if create and bool(self.created) and self.config.email:
            self.alert.send_email(self.user.email, self.data)
        return ret


class ObjectManager(Manager):
    def as_dict(self):
        result = {}
        for item in self.get_queryset():
            result[item.name] = item.target
        return result


class UserAlertObject(Model):
    alert   = ForeignKey(UserAlert, related_name='objs')
    name    = CharField(max_length=32)

    table   = ForeignKey(ContentType, **null)
    o_id    = PositiveIntegerField(null=True)
    target  = GenericForeignKey('table', 'o_id')

    objects = ObjectManager()

    def __str__(self):
        return "AlertObject %s=%d" % (self.name, self.o_id)

class UserAlertValue(Model):
    alert  = ForeignKey(UserAlert, related_name='values')
    name   = CharField(max_length=32)
    target = CharField(max_length=255)

    objects = ObjectManager()

    def __str__(self):
        return "AlertValue %s=%s" % (self.name, self.target)


class SubscriptionManager(Manager):
    def get_or_create(self, target=None, **kwargs):
        """Handle the match between a null target and non-null targets"""
        deleted = 0
        if target:
            # if subscription with no target exists, return that.
            try:
                obj = self.get(target__isnull=True, **kwargs)
            except AlertSubscription.DoesNotExist:
                return super(SubscriptionManager, self).get_or_create(target=target, **kwargs) + (0,)
            else:
                return (obj, False, deleted)

        (obj, created) = super(SubscriptionManager, self).get_or_create(target=target, **kwargs)
        if created:
            # replace all other existing subscriptions with this one.
            to_delete = self.filter(target__isnull=False, **kwargs)
            deleted = to_delete.count()
            to_delete.delete()
        return (obj, created, deleted)

    def is_subscribed(self, target=None):
        return self.filter(Q(target=target) | Q(target__isnull=True)).count()


class AlertSubscription(Model):
    alert  = ForeignKey(AlertType, related_name='subscriptions')
    user   = ForeignKey(User, related_name='alert_subscriptions')
    target = PositiveIntegerField(_("Object ID"), **null)

    objects = SubscriptionManager()

    def object(self):
        return self.alert.get_object(pk=self.target)

    def __str__(self):
        return "%s Subscription to %s" % (str(self.user), str(self.alert))


# -------- Start Example App -------- #

class Message(Model):
    """
     User messages are a simple alert example system allowing users to send messages between each other.
    """
    sender    = ForeignKey(User, related_name="sent_messages")
    recipient = ForeignKey(User, related_name="messages")
    reply_to  = ForeignKey('self', related_name="replies", **null)
    subject   = CharField(max_length=128)
    body      = TextField(_("Message Body"), validators=[MaxLengthValidator(8192)], **null)
    created   = DateTimeField(default=now)

    def get_root(self, children=None):
        """Returns the root message for the thread"""
        children = children or tuple()
        if self.reply_to:
            # Break infinate root-to-branch loop in tree
            if id(self) in children:
                return self
            return self.reply_to.get_root(children+(id(self),))
        return self

    def __str__(self):
        return "Message from %s to %s @ %s" % (unicode(self.sender), unicode(self.recipient), str(self.created))

