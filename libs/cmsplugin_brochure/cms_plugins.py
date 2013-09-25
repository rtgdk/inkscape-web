from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from cmsplugin_brochure.models import BrochurePlugin, BrochureItem
from cmsplugin_brochure import settings

from cms.utils import get_language_from_request



class CMSBrochurePlugin(CMSPluginBase):
    model = BrochurePlugin
    name = _('Gallery Brochure')
    render_template = "brochure/list.html"

    def render(self, context, instance, placeholder):
        if(not instance.source):
            items = BrochureItem.objects.all()
        else:
            help(instance.source)
            items = instance.source.brochureitem_set.all()

        context.update({
            'instance'   : instance,
            'placeholder': placeholder,
            'source'     : instance.source,
            'items'      : items.filter(enabled=True).order_by('-publish'),
        })
        return context

plugin_pool.register_plugin(CMSBrochurePlugin)


