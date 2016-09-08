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

from djangocms_text_ckeditor.widgets import TextEditorWidget
from registration.forms import RegistrationForm
from captcha.fields import ReCaptchaField

from .models import User, Team

class TeamForm(ModelForm):
    class Meta:
        exclude = ()
        model = Team

    def __init__(self, *args, **kw):
        super(TeamForm, self).__init__(*args, **kw)

        for field in ('desc', 'charter', 'side_bar'):
            if field in self.fields:
                self.fields[field].widget = TextEditorWidget()


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
    ircpass = CharField(widget=PasswordInput(), required=False)

    class Meta:
        model = User
        exclude = ('user_permissions', 'is_superuser', 'groups', 'last_login',
                   'is_staff', 'is_active', 'date_joined', 'visits', 'last_seen',
                   'password')

    def fieldsets(self):
        d = dict((field.name, field) for field in self)
        yield _("Account Settings"), [ d[k]
            for k in ['username', 'email', 'password1', 'password2', 'language']]
        yield _("Personal Details"), [ d[k]
            for k in ['first_name', 'last_name', 'bio', 'photo', 'gpg_key']]
        yield _("Social Settings"), [ d[k]
            for k in ['ircnick', 'dauser', 'ocuser', 'tbruser']] # ircpass

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
        
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        first_name = first_name.strip()
        return first_name
      
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        last_name = last_name.strip()
        return last_name

    def save(self, **kwargs):
        password = self.cleaned_data.get('password', None)
        if password:
            self.instance.set_password(password)
        ModelForm.save(self, **kwargs)


