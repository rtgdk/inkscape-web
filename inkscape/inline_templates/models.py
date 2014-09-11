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

import os
import json

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.base import *
from django.db.models import *
from django.template import *

null = {'null':True, 'blank':True}


def render_directly(template, context):
    if type(context) is not Context:
        context = Context(context or {})
    try:
        templated = Template(template)
        return templated.render(context)
    except (VariableDoesNotExist, TemplateSyntaxError) as error:
        raise ValueError(str(error))


class InlineTemplate(Model):
    name  = CharField(_("Identifyable Name"), max_length=64)
    base  = CharField(_("Test Base Template"), max_length=128, **null)

    code  = TextField(_("Template Code"))
    data  = TextField(_("Preview Data"), **null)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('preview_template', kwargs={'template_id':str(self.id)})

    def loaded_data(self, data=None):
        if not data:
            ret = json.loads(self.data)
            if type(ret) is not dict:
                return {}
        return data

    def render(self, data=None, test=False):
        code = self.code
        if test and self.base:
            (name, block) = self.base.split('|')
            code = "{%% extends \"%s\" %%}\n{%% block %s %%}\n%s\n{%% endblock %%}" % (name, block, self.code)
        return render_directly(code, self.loaded_data(data))

    def get_template(self):
        return Template(self.code)

