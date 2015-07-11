#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#

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

class ShieldAdmin(AjaxSelectAdmin):
    model   = ShieldPlugin
    inlines = [TabInline]


site.register(ShieldPlugin, ShieldAdmin)

