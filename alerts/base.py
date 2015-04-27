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

__all__ = ['ALERT_CATEGORIES', 'has_template', 'get_template', 'render_directly']

from django.template import *
from django.template.base import *
from django.template.loader import (
    TemplateDoesNotExist, template_source_loaders, get_template as load_loaders
)

import os

ALERT_CATEGORIES = (
  ('?', 'Unknown'),
  ('U', 'User to User'),
  ('S', 'System to User'),
  ('A', 'Admin to User'),
  ('P', 'User to Admin'),
  ('T', 'System to Translator'),
)
for (m, name) in ALERT_CATEGORIES:
    name = 'CATEGORY_'+name.replace(' ', '_').upper()
    locals()[name] = m
    __all__.append(name)

def has_template(template_name):
    """We load a template name and return it's contents rather than a Template object"""
    global template_source_loaders

    # Try and use as much of the django logic as possible
    if not template_source_loaders:
        try:
            load_loaders(template_name)
        except TemplateDoesNotExist:
            return None
        from django.template.loader import template_source_loaders

    for loader in template_source_loaders:
        for filename in loader.get_template_sources(template_name):
            # They should always exist, but check for weird template loaders
            return filename
    return None

def get_template(template_name):
    filename = has_template(template_name)
    if filename and os.path.isfile(filename):
        with open(filename, 'r') as fhl:
            return fhl.read()
    raise TemplateDoesNotExist(template_name)


def render_directly(template, context):
    if type(context) is not Context:
        context = Context(context or {})
    if 'i18n' not in template:
        template = "{% load i18n %}\n" + template
    try:
        templated = Template(template)
        return templated.render(context)
    except (VariableDoesNotExist, TemplateSyntaxError) as error:
        raise ValueError(str(error))


