from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from . import models

class CMSGroupPhotoPlugin(CMSPluginBase):
    model = models.GroupPhotoPlugin
    name = _('Group of Users List')
    render_template = "users/group.html"
    text_enabled = True

    def render(self, context, instance, placeholder):
        self.instance = instance
        if instance and instance.style:
            self.render_template = 'users/group-%s.html' % instance.style

        context.update({
            'users'      : instance.source.user_set.all(),
            'instance'   : instance,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSGroupPhotoPlugin)


