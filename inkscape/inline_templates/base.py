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
Provides an inline template editor, simple way to make the front end controlable.
This would be something the cms could do, but it'd need more in the way of variable
controls in their system and they just don't have that yet.
"""

from django.template import *
from django.template.base import *


def render_directly(template, context):
    if type(context) is not Context:
        context = Context(context or {})
    try:
        templated = Template(template)
        return templated.render(context)
    except (VariableDoesNotExist, TemplateSyntaxError) as error:
        raise ValueError(str(error))


