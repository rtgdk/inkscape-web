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

from HTMLParser import HTMLParser
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from django.conf import settings

from .models import TableOfContents


class TocParser(HTMLParser):
    def get_toc(self, body):
        self.head = None
        self.toc = []
        self.feed(body)

        ret = {'children':[], 'level': -1}
        parents = [ret]
        for item in self.toc:
            child = { 'title': item['title'] or _('Untitled Section'), 'id': item.get('id', None), 'children': [] }
            while item['level'] <= parents[-1]['level']:
                parents.pop()
            parents[-1]['children'].append(child)
            parents.append({'children': child['children'], 'level': item['level']})
        return ret['children']

    def handle_starttag(self, tag, attrs):
        if tag[0] == 'h':
            attrs = dict(attrs)
            attrs['level'] = int(tag[1])
            attrs['title'] = ''
            self.head = attrs

    def handle_endtag(self, tag):
        if tag[0] == 'h':
            self.toc.append( self.head )
            self.head = None

    def handle_data(self, data):
        if self.head:
            self.head['title'] += unicode(data)


class TableOfContentsPlugin(CMSPluginBase):
    model = TableOfContents
    name = _("Table of Contents")
    render_template = "cms/plugins/toc.html"
    allow_children = False
    text_enabled = True

    def _tree(self, instance):
        if instance.parent:
            # TOC is based on parent contents only
            plugins = [ instance.parent.get_plugin_instance()[0] ]
        else:
            # TOC is based on ALL available plugins
            plugins = [ plugin.get_plugin_instance()[0] \
                for place in instance.page.placeholders.all() \
                for plugin in place.get_plugins(instance.language) ]

        # We'll do something much smarter in the future
        toc = TocParser().get_toc(plugins[0].body)
        return toc

    def render(self, context, instance, placeholder):
        context.update({
            'placeholder': placeholder,
            'plugin'     : instance,
            'children'   : self._tree(instance),
        })
        return context


plugin_pool.register_plugin(TableOfContentsPlugin)
