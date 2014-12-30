
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import *
from django.forms import *

from .models import *

from ajax_select import make_ajax_field
from ajax_select.admin import AjaxSelectAdmin

class TabForm(ModelForm):
    user  = make_ajax_field(Tab, 'user', 'user', help_text=_('Select Author\'s User Account'))

    class Meta:
        fields = ('order','tab_name','tab_text','tab_cat','name','download','user','license','link','banner_text','banner_foot','btn_text','btn_link','btn_icon')
        labels = {
          'name':     _('Background Image Name'),
          'download': _('Background Image File'),
          'user':     _('Background Author'),
          'license':  _('Background License'),
          'link':     _('Background Credit Link'),
        }

site.register(Tab)
site.register(TabCategory)

class TabInline(StackedInline):
    form  = TabForm
    model = Tab
    extra = 1

class ShieldAdmin(ModelAdmin):
    model   = ShieldPlugin
    inlines = [TabInline]


site.register(ShieldPlugin, ShieldAdmin)

