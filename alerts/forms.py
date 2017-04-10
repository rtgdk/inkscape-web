#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
Forms for the alert system 
"""

from django.forms import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from inkscape.utils import to
from .models import Message, AlertType, AlertSubscription, UserAlertSetting

class MessageForm(ModelForm):
    reply_to = IntegerField(widget=HiddenInput, required=False)
    recipient = IntegerField(widget=HiddenInput)

    class Meta:
        model = Message
        fields = ('subject','body', 'recipient', 'reply_to')

    def clean_recipient(self):
        pk = self.cleaned_data['recipient']
        return get_user_model().objects.get(pk=pk)

    def clean_reply_to(self):
        pk = self.cleaned_data['reply_to']
        if pk:
            return Message.objects.get(pk=pk)


class SettingsBaseFormSet(BaseModelFormSet):
    def __init__(self, instance, *args, **kw):
        self.user = instance
        super(SettingsBaseFormSet, self).__init__(*args, **kw)

    @to(list)
    def get_queryset(self):
        """Return a fixed list of alert_settings (not a queryset)"""
        for alert in AlertType.objects.all().order_by('slug'):
            if not alert.permission or self.user.has_perm(alert.permission):
                if alert.show_settings:
                    yield alert.settings.for_user(self.user)

    def _construct_form(self, i, **kwargs):
        # Link POST forms to their alert_types, so override when is_bound.
        if self.is_bound and i < self.initial_form_count():
            alert_id = self.data["%s-%s" % (self.add_prefix(i), 'alert')]
            for obj in self.get_queryset():
                if str(obj.alert_id) == str(alert_id):
                    kwargs['instance'] = obj
            # Note use of parent's parent construct_form call here.
            return super(BaseModelFormSet, self)._construct_form(i, **kwargs)
	return super(SettingsBaseFormSet, self)._construct_form(i, **kwargs)



class SettingsForm(ModelForm):
    suball = BooleanField(required=False, label=_("Subscribe to All"),
        help_text=_("<strong>Warning!</strong> This can result in a lot of messages."))
    em_msg = _("<strong>Warning!</strong> You haven't told us your mail addres"
               "s yet! If you would like to receive emails from inkscape.org, "
               "enter an email address <a href='%(url)s'>in your profile</a>.")

    class Meta:
        model = UserAlertSetting
        fields = ('alert', 'email', 'irc', 'batch', 'owner', 'suball')

    def __init__(self, *args, **kw):
        super(SettingsForm, self).__init__(*args, **kw)
        self.fields['alert'].widget = HiddenInput()
        self.subs = self.instance.subscriptions

        # XXX Replace with "disabled" class and change help_text
        if not self.instance.user.ircnick:
            self.fields.pop('irc')
        if not self.instance.user.email:
            self.fields['email'].widget.attrs['disabled'] = 'disabled'
            self.fields['email'].help_text = self.em_msg % {'url': reverse('edit_profile')}
        if not self.instance.alert.subscribe_own:
            self.fields.pop('owner')
            # XXX the name of this field needs to change depending on if subscribe is visible at all.
        if self.instance.alert.subscribe_all:
            self.suball = self.subs.filter(target__isnull=True)
            self.fields['suball'].initial = self.suball.count() == 1
        else:
            self.fields.pop('suball')

        if self.instance.alert.subscribe_any:
            for sub in self.subs.filter(target__isnull=False):
                label = _("Subscription to %s") % unicode(sub.object())
                field = BooleanField(required=False, label=label)
                field.delete = True
                self.fields['delete_%d' % sub.pk] = field

    def save(self, commit=True, **kw):
        ret = super(SettingsForm, self).save(commit=commit, **kw)
        if commit:
            if self.instance.alert.subscribe_all:
                if self.cleaned_data.get('suball', False):
                    self.subs.get_or_create(None, alert_id=self.instance.alert_id, user_id=self.instance.user_id)
                else:
                    self.subs.filter(target__isnull=True).delete()
            if self.instance.alert.subscribe_any:
                for obj in self.subs.filter(target__isnull=False):
                    obj.delete()
        return ret

    @property
    def label(self):
        if not self.instance.pk:
            return unicode(self.instance) + "*"
        return unicode(self.instance)

    @property
    def description(self):
        return self.instance.alert.info


SettingsFormSet = modelformset_factory(
    model=UserAlertSetting,
    form=SettingsForm,
    formset=SettingsBaseFormSet, extra=0)

