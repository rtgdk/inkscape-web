from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models
from . import settings


class CMSBugCountPlugin(CMSPluginBase):
    model = models.BugCountPlugin
    name = _('Launchpad Bug Count')
    render_template = "launchpad/count.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        self.instance = instance

        context.update({
            'instance'   : instance,
            'placeholder': placeholder,
            'counter'    : instance.source,
            'count'      : instance.source.count(),
            'importance' : instance.importance(),
        })
        return context

plugin_pool.register_plugin(CMSBugCountPlugin)


