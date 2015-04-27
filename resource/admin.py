#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import *

from ajax_select import make_ajax_field
from ajax_select.admin import AjaxSelectAdmin

from .forms import ModelForm
from .models import *

site.register(License)
site.register(Category)
site.register(ResourceFile)
site.register(ResourceMirror)
site.register(Vote)

class QuotaAdmin(ModelAdmin):
    list_display = ('name', 'quota_size')

    def name(self, obj):
        if obj.group:
            return _("Quota for %s") % str(obj.group)
        return _('Quota for Everyone')

    def quota_size(self, obj):
        return filesizeformat(obj.size)

site.register(Quota, QuotaAdmin)

class GalleryForm(ModelForm):
    user  = make_ajax_field(Gallery, 'user', 'user', \
        help_text=_('Select Group\'s Owner'))

class GalleryAdmin(ModelAdmin):
    readonly_fields = ('items', 'slug')
    form = GalleryForm

site.register(Gallery, GalleryAdmin)
