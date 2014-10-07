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

from django.db.models import *

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse

from pile.models import null

from .base import render_directly, get_template



def created_alert(sender, instance, created=False, **kwargs):
     """Connect this method to the post_save signal and it will
        create an alert when the sender *creates* a new object."""
     if not created:
         return
     edited_alert(sender, instance, created, **kwargs)

def edited_alert(sender, instance, created=False, **kwargs):
     """Connect this method to the post_save signal and it will
        create an alert when the sender edits any object."""
     slug = sender.__name__.lower()
     config = dict(
         template="alerts/%s.html" % slug,
         name = _("Alert for %s") % slug,
         desc = _("No Description for alert %s") % slug
     )
     config.update( getattr(sender, 'alert_config', {}) )
     creator = getattr(instance, getattr(sender, 'alert_user', 'creator'))
     if not isinstance(creator, User):
         raise ValueError("Expected user object as recipient for alert. Found %s" % type(creator).__name__)
     alert_type = AlertType.objects.get_alert(slug, **config)
     alert_type.send_to(creator, **{slug: instance})


MSG_CAT = (
  ('?', 'Unknown'),
  ('U', 'User to User'),
  ('S', 'System to User'),
  ('A', 'Admin to User'),
  ('P', 'User to Admin'),
  ('T', 'System to Translator'),
)

class AlertManager(Manager):
    def get_alert(self, slug, template=None, **kwargs):
        """
            Will create an alert type if not available yet.
            If will also create a new AlertType if the previous AlertType is not enabled,
              this is a way of freezing the previous type and regenerating a new one without
              distrupting the messages users already have.
        """
        if template:
            (item, created) = self.get_or_create(enabled=True, slug=slug, defaults=kwargs)
            if created:
                item.set_template(template)
            return item
        try:
            return self.get(slug=slug)
        except AlertType.DoesNotExist:
            return None


class AlertType(Model):
    """All Possible messages that users can recieve, acts as a template"""
    name     = CharField(_("Type Name"),        max_length=64)
    desc     = CharField(_("Type Description"), max_length=255)
    slug     = CharField(_("URL Slug"),         max_length=32)

    group    = ForeignKey(Group, verbose_name=_("Limit to Group"), **null)

    subject  = CharField(_("Subject Template"), max_length=255)
    body     = TextField(_("Body Template"))
    
    category = CharField(_("Type Category"), max_length=1, choices=MSG_CAT, default='?')
    enabled  = BooleanField(default=False)

    # These get copied into UserAlertSettings for this alert
    default_hide  = BooleanField(default=False)
    default_email = BooleanField(default=False)

    objects = AlertManager()

    def set_template(self, template):
        """Update the alert type with a template, you can specify the template
        body directly or you can specify a template file to be cached in the database."""

        # Template contains cariage returns
        if "\n" not in template:
            # User is setting a template via filename
            template = get_template(template)

        # The first line of the template is the subject
        (subject, body) = template.split('\n', 1)

        # Except when it's not, and instead contains the name and description
        if '||' in subject:
            (self.name, self.desc) = subject.split('||', 1)
            (subject, body) = body.split('\n', 1)

        # We save all these updates (between two and four fields)
        self.subject = subject
        self.body = body
        self.save()

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
            alert = UserAlert(user=user, alert=self)
            alert.save()
            for (key, value) in kwargs.items() or ():
                UserAlertObject(alert=alert, name=key, target=value).save()
            return alert
        return None

    def __str__(self):
        return self.name


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


class UserAlertSetting(Model):
    user    = ForeignKey(User, related_name='alert_settings')
    alert   = ForeignKey(AlertType, related_name='settings')
    hide    = BooleanField(_("Hide Alerts"), default=True)
    email   = BooleanField(_("Send Email Alert"), default=False)
    
    def __str__(self):
        return "User Alert Setting"


class UserAlertManager(Manager):
    def get_query_set(self):
        return Manager.get_query_set(self).filter(deleted__isnull=True)

    def new(self):
        return self.get_query_set().filter(viewed__isnull=True)

    def types(self):
        return self.new().values('alert').annotate(count=Count('alert'))\
                  .values_list('alert__slug', 'alert__name', 'count')


class UserAlert(Model):
    """A single altert for a specific user"""
    user    = ForeignKey(User, related_name='alerts')
    alert   = ForeignKey(AlertType, related_name='sent')

    created = DateTimeField(auto_now=True)
    viewed  = DateTimeField(**null)
    deleted = DateTimeField(**null)

    objects = UserAlertManager()

    def view(self):
        if not self.viewed:
            self.viewed = now()
            self.save()

    def delete(self):
        if not self.deleted:
            self.deleted = now()
            self.reed()
            self.save()

    def is_hidden(self):
        if self.viewed or self.deleted:
            return True
        return self.config.hide

    @property
    def config(self):
        # This should auto-create but not save.
        return UserAlertSetting.objects.get(user=self.user, alert=self.alert)

    def __str__(self):
        return self.subject

    @property
    def subject(self):
        return render_directly( self.alert.subject, self.data.as_dict() )

    @property
    def body(self):
        return render_directly( self.alert.body, self.data.as_dict() )

    def send_email(self):
        # XXX Send email, todo!
        pass

    def save(self, **kwargs):
        create = not bool(self.created)
        ret = Model.save(self, **kwargs)
        # This means: We didn't exist, and now we do.
        if create and bool(self.created):
            self.send_email()
        return ret


class ObjectManager(Manager):
    def as_dict(self):
        result = {}
        for item in self.get_query_set():
            result[item.name] = item.target
        return result


class UserAlertObject(Model):
    alert = ForeignKey(UserAlert, related_name='data')
    name  = CharField(max_length=32)

    table  = ForeignKey(ContentType, **null)
    o_id   = PositiveIntegerField(null=True)
    target = GenericForeignKey('table', 'o_id')

    objects = ObjectManager()


# -------- Start Example App -------- #


class Message(Model):
    """
     User messages are a simple alert example system allowing users to send messages between each other.
    """
    sender    = ForeignKey(User, related_name="sent_messages")
    recipient = ForeignKey(User, related_name="messages")
    reply_to  = ForeignKey('self', related_name="replies", **null)
    subject   = CharField(max_length=128)
    body      = TextField(_("Message Body"), **null)
    created   = DateTimeField(default=now)

    alert_user = 'recipient'

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


signals.post_save.connect(created_alert, sender=Message, dispatch_uid="message")

