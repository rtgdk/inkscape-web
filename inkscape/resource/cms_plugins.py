from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.utils.permissions import get_current_user as get_user

from .forms import ModelForm
from .models import Q, GalleryPlugin, CategoryPlugin

from inkscape.settings import DEBUG

class GalleryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(GalleryForm, self).__init__(*args, **kwargs)
        source = self.fields['source']
        source.queryset = source.queryset.filter(Q(user=get_user())|Q(group__in=get_user().groups.all()))

    
class CMSCategoryPlugin(CMSPluginBase):
    model = CategoryPlugin
    name  = _('InkSpace Category')
    cache = DEBUG

    def render(self, context, instance, placeholder):
        items = instance.source.items.filter(published=True)
        context.update({
            'placeholder': placeholder,
            'items'      : items.order_by('-edited'),
            'limit'      : instance.limit,
        })
        return context


class CMSGalleryPlugin(CMSCategoryPlugin):
    model = GalleryPlugin
    name  = _('InkSpace Gallery')
    form  = GalleryForm


plugin_pool.register_plugin(CMSGalleryPlugin)
plugin_pool.register_plugin(CMSCategoryPlugin)

