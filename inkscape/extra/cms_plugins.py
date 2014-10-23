from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from inkscape.settings import DEBUG

from django.contrib.admin import *
from .models import *
from .admin import TabInline

class CMSShieldPlugin(CMSPluginBase):
    inlines = [TabInline]
    model   = ShieldPlugin
    name    = _('Front Shield')
    cache   = not DEBUG

    def render(self, context, instance, placeholder):
        context.update({
            'placeholder': placeholder,
            'tabs'       : instance.tabs.all(),
            'instance'   : instance
        })
        return context



plugin_pool.register_plugin(CMSShieldPlugin)

