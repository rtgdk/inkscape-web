
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import *
from django.forms import *

from .models import *

class TabForm(ModelForm):
    class Meta:
        fields = ('order','tab_name','tab_text','tab_cat','name','download','user','license','link','banner_text','banner_foot','btn_text','btn_link','btn_icon')
        labels = {
          'name':     _('Banner Title'),
          'download': _('Banner File'),
          'user':     _('Banner Author'),
          'license':  _('Banner License'),
          'link':     _('Banner Link'),
        }

site.register(Tab)
site.register(TabCategory)

class TabInline(StackedInline):
    model = Tab
    form  = TabForm
    extra = 1

class ShieldAdmin(ModelAdmin):
    model   = ShieldPlugin
    inlines = [TabInline]


site.register(ShieldPlugin, ShieldAdmin)

