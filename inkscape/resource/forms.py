#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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
Forms for the gallery system
"""
from django.forms import *
from django.utils.translation import ugettext_lazy as _

from .models import Resource


class ResourceForm(ModelForm):
    permission = BooleanField(label=_('I have permission to post this work'))

    class Meta:
        model = Resource
        exclude = ('created', 'edited', 'user')

    def clean(self):
        if self.cleaned_data.get('permission') != True and self.cleaned_data.get('owner') == False:
            raise ValidationError("You need to have permission to post this work, or be the owner of the work.")
        return self.cleaned_data


