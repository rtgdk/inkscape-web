from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import GalleryPlugin, CategoryPlugin

from inkscape.settings import DEBUG

class CMSGalleryPlugin(CMSPluginBase):
    render_template = "resource/list.html"
    model = GalleryPlugin
    name  = _('InkSpace Gallery')
    cache = DEBUG

    def render(self, context, instance, placeholder):
        items = instance.source.items.filter(published=True)
        context.update({
            'instance'   : instance,
            'placeholder': placeholder,
            'items'      : items.order_by('-edited'),
            'limit'      : instance.limit,
        })
        return context

class CMSCategoryPlugin(CMSGalleryPlugin):
    model = CategoryPlugin
    name  = _('InkSpace Category')


plugin_pool.register_plugin(CMSGalleryPlugin)
plugin_pool.register_plugin(CMSCategoryPlugin)

