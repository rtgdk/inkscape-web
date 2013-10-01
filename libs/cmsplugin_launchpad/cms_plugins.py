from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models
from . import settings


class CMSBugPlugin(CMSPluginBase):
    model = models.BugPlugin
    name = _('Launchpad Bug Report')

    @property
    def render_template(self):
        return self.instance.template

    def render(self, context, instance, placeholder):
        self.instance = instance

        items = instance.source.bugitem_set.all()

        context.update({
            'instance'   : instance,
            'placeholder': placeholder,
            'source'     : instance.source,
            'items'      : items.order_by('-publish')[:instance.limit],
            'count'      : items.count(),
        })
        return context

plugin_pool.register_plugin(CMSBugPlugin)


