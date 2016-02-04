#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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
Provides template functions as easy to use methods.
"""

__all__ = ['has_template', 'get_template', 'render_template', 'render_directly']

import os

from django.template import *
from django.template.base import *
from django.template.loader import get_template

def has_template(template_name):
    """We load a template name and return its contents rather than a Template object"""
    try:
        return bool(get_template(template_name))
    except TemplateDoesNotExist:
        return False

def render_template(template_name, context):
    template = get_template(template_name)
    return render_directly(template, context)

def render_directly(template, context):
    if type(context) is not Context:
        context = Context(context or {})
    if isinstance(template, (str, unicode)):
        template = "{% load i18n %}" + template
        template = Template(template)
    try:
        return template.render(context)
    except (VariableDoesNotExist, TemplateSyntaxError) as error:
        raise ValueError(str(error))


