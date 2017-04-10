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
Inherit from these classes if you want to create your own alert connections.
"""
__all__ = ['BaseAlert', 'EditedAlert', 'CreatedAlert']

from django.conf import settings
from django.dispatch import receiver
from django.db.models import Model, Q, signals as django_signals
from django.core.mail.message import EmailMultiAlternatives
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from alerts.template_tools import has_template, render_template, render_directly

from signal import SIGUSR1
import os

ALL_ALERTS = {}

class Lookup(object):
    """This descriptor is a class and object property, this is so
       we can do things like:

       Message.subscriptions.all()
       msgobj.subscriptions.all()
    """
    def __init__(self, base, model):
        self.base = base
        self.model = model

    def __get__(self, obj, klass=None):
        """Get a normal manager, but add in an extra attributes"""
        manager = type(self.model.objects)()
        manager.target = obj
        manager.model = self.model
        manager.alert_type = self.base.alert_type
        return manager

class BaseAlert(object):
    """None model parent class for your alert signals"""
    # Control how subscriptions will work.
    subscribe_all = True
    subscribe_any = True
    subscribe_own = True # Related users and groups

    # These defaults control how messages should be displayed or
    # Send via email to the user's email address.
    default_email = True
    default_irc   = False
    default_batch = None  # Instant

    signal   = django_signals.post_save
    sender   = None

    # What lookup should be attached to the sender model;
    # much like ForeignKey related_name it creates reverse lookups.
    related_name = 'alerts'
    related_sub  = 'subscriptions'

    subject  = "{{ instance }}"
    email_subject = "{% trans 'Website Alert:' %} {{ instance }}"
    email_footer = 'alerts/alert/email_footer.txt'
    object_name = "{{ instance }}"

    # User specifies which user attribute on the instance alerts are sent
    alert_user  = '.'
    alert_group = '.'

    # Should we load only on test suite run.
    test_only = False

    # Should settings be disabled and the defaults for all
    show_settings = True

    # Is there a permission requirement to see this setting
    permission = None

    # Target is the attribute on the instance which subscriptions are bound
    target_field = None

    def __new__(cls, slug, *args, **kw):
        # Global registration so this is a singleton.
        if slug not in ALL_ALERTS:
            ALL_ALERTS[slug] = super(BaseAlert, cls).__new__(cls, slug, *args, **kw)
            #raise KeyError("Alert can not be registered twice: %s" % slug)
        return ALL_ALERTS[slug]

    def __init__(self, slug, is_test=False, is_migrate=False, **kwargs):
        if hasattr(self, 'slug'):
            # Already initialised (just passed in from __new__)
            return;

        self.slug = slug
        self.is_test = is_test
        self.is_migrate = is_migrate
        self.connected = False

        # Check the setup of this alert class
        if not self.sender:
            raise AttributeError("%s required 'sender' attribute" %
                type(self).__name__)
        if hasattr(self.sender, self.related_name):
            raise AttributeError("%s already has '%s' reverse lookup" % (
                self.sender.__name__, self.related_name))

        super(BaseAlert, self).__init__(**kwargs)

        if not self.is_test:
            from alerts.models import AlertType
            if not self.is_migrate:
                # Create an AlertType object which mirrors this class
                (self._alert_type, _) = AlertType.objects.get_or_create(
                  slug=self.slug,
                  values={
                    'enabled': True,
                    'default_email' : self.default_email,
                    'default_irc': self.default_irc,
                    'default_batch': self.default_batch,
                  })
            self.connect_signals()

        def look_up(fn):
            def _inner(cls, obj=None):
                if obj is None and isinstance(cls, Model):
                    obj = cls
                return fn(obj)

        from alerts.models import UserAlert, AlertSubscription
        setattr(self.sender, self.related_name, Lookup(self, UserAlert))
        setattr(self.sender, self.related_sub, Lookup(self, AlertSubscription))

    def connect_signals(self):
        """Attempts to start the signals late"""
        if not self.connected:
            self.signal.connect(self.call, sender=self.sender, dispatch_uid=self.slug)
            self.connected = True
        return self

    def disconnect_signals(self):
        """Disconnects the alert signal, useful for tests"""
        if self.connected:
            self.signal.disconnect(self.call, sender=self.sender, dispatch_uid=self.slug)
            self.connected = False
        return self

    @property
    def alert_type(self):
        """For tests we have to load alert_type object's late (to cope with loaddata fixture issues)"""
        if not hasattr(self, '_alert_type'):
            # This will fail is the test doesn't include a fixture with all the right
            # alert types available. It depends on the test to populate the database.
            from alerts.models import AlertType
            self._alert_type = AlertType.objects.get(slug=self.slug)
        return self._alert_type

    def get_alert_users(self, instance):
        """Returns a user of a list of users to send emails to"""
        return getattr(instance, self.alert_user, None)

    def get_alert_groups(self, instance):
        """Returns a group or a list of groups to send emails to"""
        return getattr(instance, self.alert_group, None)

    def call(self, sender, signal=None, **kwargs):
        """Connect this method to the post_save signal and it will
           create an alert when the sender edits any object."""
        def send_to(recipient, kind=None):
             if kind is None or isinstance(recipient, kind):
                 return self.alert_type.send_to(recipient, **kwargs)

        instance = kwargs['instance']

        if self.subscribe_own:
            send_to(self.get_alert_users(instance), get_user_model())
            send_to(self.get_alert_groups(instance), Group)

        if self.subscribe_all:
            for sub in self.alert_type.subscriptions.filter(target__isnull=True):
                send_to(sub.user)

        if self.subscribe_any:
            target = instance
            if self.target_field:
                target = getattr(instance, self.target_field)

            for sub in self.alert_type.subscriptions.filter(target=target.pk):
                send_to(sub.user)

        # TODO: send_to returns a list of users sent to, but we don't log much here.
        return True

    @property
    def instance_type(self):
        if self.target_field:
            return self.sender._meta.get_field(self.target_field).rel.to
        return self.sender

    @property
    def template(self):
        n = "%s/alert/%s.html" % tuple(self.slug.split('.', 1))
        if has_template(n):
            return n
        import sys
        sys.stderr.write("Couldn't find: %s\n" % str(n))
        return "alerts/type_default.html"

    @property
    def email_template(self):
        n = "%s/alert/email_%s.txt" % tuple(self.slug.split('.', 1))
        if has_template(n):
            return n
        import sys
        sys.stderr.write("Couldn't find: %s\n" % str(n))
        return "alerts/email_default.txt"

    @property
    def name(self):
        raise NotImplementedError("Name is a required property for alerts.")

    @property
    def desc(self):
        raise NotImplementedError("Desc is a required property for alerts.")

    @property
    def info(self):
        raise NotImplementedError("Info is a required property for alerts.")

    def get_object(self, **fields):
        """Returns object matching field using Alert's target object type"""
        model = self.sender
        if self.target_field:
            # Get FoeignKey's mdel linking this alert instead
            model = getattr(model, self.target_field).field.rel.to
        return model.objects.get(**fields)

    def get_object_name(self, obj):
        """Return's a label for this kind of subscription for an object"""
        if obj:
            return render_directly(self.object_name, {'object': obj})
        return None

    def format_data(self, data):
        """Overridable function to format data for the template"""
        return data

    def get_subject(self, context_data):
        return render_directly(self.subject, self.format_data(context_data))

    def get_body(self, context_data):
        return render_template(self.template, context_data)

    def send_irc_msg(self, user):
        """
        Send the running IRC bot a kick up the bum about a new alert.
        """
        try:
            with open(settings.IRCBOT_PID, 'r') as pid:
                pid = int(pid.read().strip())
            with open('/proc/%d/cmdline' % pid, 'r') as proc:
                assert('ircbot' in proc.read())
            os.kill(pid, SIGUSR1)
            return True
        except:
            # Any errors may mean:
            # * IRCBOT not configured, not running
            # * IRCBOT pid file exists but process isn't ircbot
            # * We don't have permission to signal process
            return False

    def send_email(self, recipient, context_data, **kwargs):
        if not recipient:
            return False

        context_data = self.format_data(context_data)
        subject = render_directly(self.email_subject, context_data)

        kwargs.update({
            'subject': subject.strip().replace('\n', ' ').replace('\r', ' '),
            'body': render_template(self.email_template, context_data),
            'to': [recipient],
        })

        if self.email_footer is not None:
            kwargs['body'] += render_template(self.email_footer, context_data)

        #if self.alert_type.CATEGORY_USER_TO_USER:
        #    this doesn't work yet because we don't know how to get the sender
        #    kwargs['reply_to'] = self.get_sender(context_data)

        # This will fail silently if not configured right
        return EmailMultiAlternatives(**kwargs).send(True)


class EditedAlert(BaseAlert):
    def call(self, sender, instance, **kwargs):
        if not kwargs.get('created', False):
            return super(EditedAlert, self).call(sender, instance=instance, **kwargs)
        return False


class CreatedAlert(BaseAlert):
    def call(self, sender, instance, **kwargs):
        if kwargs.get('created', False):
            return super(CreatedAlert, self).call(sender, instance=instance, **kwargs)
        return False

#@receiver(django_signals.pre_delete)
def objects_deleted(sender, instance, **kwargs):
    """
    Check our alert objects for deleted items and clean up
    """
    return # XXX Disabled for now.

    from alerts.models import UserAlertObject
    ct = ContentType.objects.get_for_model(type(instance))

    # django-cms does a lot of deleting, we want to ignore it
    #global KNOWN_TYPES
    #if not KNOWN_TYPES:
    #    KNOWN_TYPES = UserAlertValue.objects.values_list('table_id', flat=True).distinct()
    #if ct.pk not in KNOWN_TYPES:
    #    return

    try:
        qs = UserAlertObject.objects.filter(o_id=instance.pk, table=ct)
        for obj in qs:
            obj.alert.values.create(name='%s_deleted' % obj.name, target=unicode(instance))
        qs.delete()
    except ValueError:
        pass # I have no idea why this error happens.

