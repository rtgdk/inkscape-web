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
Protect InlineTemplate from coding errors.
"""

from django.forms import *

from .models import InlineTemplate
from .base import render_directly

from splitjson.widgets import SplitJSONWidget

class TemplateForm(ModelForm):
    data = CharField(widget=SplitJSONWidget())

    class Meta:
        model = InlineTemplate

    def clean_code(self):
        ret = self.cleaned_data['code']
        try:
            render_directly(ret, {})
        except ValueError as error:
            raise ValidationError(str(error))
        return ret

    def clean_data(self):
        # XXX Here we can use some tricks to get all the
        # vars from the template and make sure they're in the
        # test data
        return self.cleaned_data['data']

