#
# Copyright (C) 2015  Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Table of contents plugin to django-cms. Automatically loaded by django-cms.
"""

from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from django.conf import settings

from .models import TableOfContents

class TableOfContentsPlugin(CMSPluginBase):
    model = TableOfContents
    name = _("Table of Contents")
    render_template = "cms/plugins/toc.html"
    allow_children = False
    text_enabled = True

    def icon_src(self, instance):
        return settings.STATIC_URL + "images/cms/toc.svg"

    def icon_alt(self, instance):
        return "Table of Contents"

    def render(self, context, instance, placeholder):
        context.update({
            'placeholder': placeholder,
            'plugin'     : instance,
        })
        return context


plugin_pool.register_plugin(TableOfContentsPlugin)
