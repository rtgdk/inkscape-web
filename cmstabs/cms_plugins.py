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
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.admin import *
from django.conf import settings

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import *
from .admin import TabInline

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

class InlinePagesPlugin(CMSPluginBase):
    model = InlinePages
    name = "Inline Pages (tabs)"
    render_template = "cms/plugins/inline_pages.html"
    allow_children = True
    child_classes = ["InlinePagePlugin"]

    def render(self, context, instance, placeholder):
        context.update({ 'instance': instance })
        return context


class InlinePagePlugin(CMSPluginBase):
    model = InlinePage
    name = "Single Inline Page"
    render_template = "cms/plugins/inline_page.html"
    parent_classes = ["InlinePagesPlugin"]
    allow_children = True

    def render(self, context, instance, placeholder):
        context.update({ 'instance': instance })
        return context

plugin_pool.register_plugin(InlinePagesPlugin)
plugin_pool.register_plugin(InlinePagePlugin)

class CMSShieldPlugin(CMSPluginBase):
    inlines = [TabInline]
    model   = ShieldPlugin
    name    = _('Front Shield')
    cache   = settings.ENABLE_CACHING

    render_template = "cms/plugins/shield.html"

    def render(self, context, instance, placeholder):
        context.update({
            'placeholder': placeholder,
            'tabs'       : instance.tabs.all(),
            'instance'   : instance
        })
        return context

plugin_pool.register_plugin(CMSShieldPlugin)

class CMSGroupBioPlugin(CMSPluginBase):
    model = GroupPhotoPlugin
    name = _('Group of Users List')
    render_template = "cms/plugins/group.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        self.instance = instance
        if instance and instance.style:
            self.render_template = 'cms/plugins/group-%s.html' % instance.style

        context.update({
            'users'      : instance.source.user_set.all(),
            'instance'   : instance,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSGroupBioPlugin)

class InkPicturePlugin(CMSPluginBase):
    model = InkPicture
    name = _("InkPicture")
    render_template = "cms/plugins/inkpicture.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        if instance.url:
            link = instance.url
        elif instance.page_link:
            link = instance.page_link.get_absolute_url()
        else:
            link = ""
        context.update({
            'picture': instance,
            'link': link,
            'placeholder': placeholder
        })
        return context

    def icon_src(self, instance):
        if getattr(settings, 'PICTURE_FULL_IMAGE_AS_ICON', False):
            return instance.image.url
        else:
            return urlparse.urljoin(
                settings.STATIC_URL, "cms/img/icons/plugins/inkpicture.png")

plugin_pool.register_plugin(InkPicturePlugin)