
from django.forms import *
from .models import User, UserDetails
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationForm
from captcha.fields import ReCaptchaField

class RegisForm(RegistrationForm):
    recaptcha = ReCaptchaField(label=_("Human Test"))

class UserForm(ModelForm):
    password1 = CharField(label=_('Password'), widget=PasswordInput(), required=False)
    password2 = CharField(label=_('Confirm'), widget=PasswordInput(), required=False)

    class Meta:
        model = User
        exclude = ('user_permissions', 'is_superuser', 'groups', 'last_login',
                   'is_staff', 'is_active', 'date_joined')
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password1 != password2:
            raise ValidationError("Passwords don't match")


        return self.cleaned_data

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username)
        if user and user[0] != self.instance:
            raise ValidationError('Username already taken')
        return username
        

    def save(self):
        password = self.cleaned_data.get('password1')
        if password:
            self.instance.set_password(password)
        ModelForm.save(self)

class UserDetailsForm(ModelForm):
    ircpass = CharField(widget=PasswordInput(), required=False)

    class Meta:
        model = UserDetails
        exclude = ('user','last_seen','visits')

