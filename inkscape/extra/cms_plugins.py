from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from inkscape.settings import DEBUG

from django.contrib.admin import *
from .models import *
from .admin import TabInline

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
    cache   = not DEBUG

    render_template = "cms/plugins/shield.html"

    def render(self, context, instance, placeholder):
        context.update({
            'placeholder': placeholder,
            'tabs'       : instance.tabs.all(),
            'instance'   : instance
        })
        return context



plugin_pool.register_plugin(CMSShieldPlugin)

