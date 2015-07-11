#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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

from django.forms import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Permission

from registration.forms import RegistrationForm
from captcha.fields import ReCaptchaField

from .models import User, UserDetails

class PasswordForm(PasswordResetForm):
    recaptcha = ReCaptchaField(label=_("Human Test"))

class RegisForm(RegistrationForm):
    recaptcha = ReCaptchaField(label=_("Human Test"))

class AgreeToClaForm(Form):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super(AgreeToClaForm, self).__init__(*args, **kwargs)

    def save(self):
        cla = Permission.objects.get(codename='website_cla_agreed')
        self.instance.user_permissions.add(cla)
        return self.instance


class UserForm(ModelForm):
    password1 = CharField(label=_('Password'), widget=PasswordInput(), required=False)
    password2 = CharField(label=_('Confirm'), widget=PasswordInput(), required=False)

    class Meta:
        model = User
        exclude = ('user_permissions', 'is_superuser', 'groups', 'last_login',
                   'is_staff', 'is_active', 'date_joined')
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Passwords don't match")
            self.cleaned_data['password'] = password1


        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username)
        if user and user[0] != self.instance:
            raise ValidationError('Username already taken')
        return username
        

    def save(self, **kwargs):
        password = self.cleaned_data.get('password', None)
        if password:
            self.instance.set_password(password)
        ModelForm.save(self, **kwargs)

class UserDetailsForm(ModelForm):
    ircpass = CharField(widget=PasswordInput(), required=False)

    class Meta:
        model = UserDetails
        exclude = ('user','last_seen','visits')

from .multiform import MultiModelForm

class PersonForm(MultiModelForm):
    base_forms = [
        ('self', UserForm),
        ('details', UserDetailsForm),
    ]

