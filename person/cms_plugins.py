from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import GroupPhotoPlugin

class CMSGroupBioPlugin(CMSPluginBase):
    model = GroupPhotoPlugin
    name = _('Group of Users List')
    render_template = "person/plugin/group.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        self.instance = instance
        if instance and instance.style:
            self.render_template = 'person/plugin/group-%s.html' % instance.style

        context.update({
            'users'      : instance.source.user_set.all(),
            'instance'   : instance,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSGroupBioPlugin)


