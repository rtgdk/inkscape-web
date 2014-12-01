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

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from django.template.defaultfilters import filesizeformat

from .models import *

admin.site.register(License)
admin.site.register(Category)
admin.site.register(ResourceFile)
admin.site.register(ResourceMirror)
admin.site.register(Gallery)
admin.site.register(Vote)

class QuotaAdmin(admin.ModelAdmin):
    list_display = ('name', 'quota_size')

    def name(self, obj):
        if obj.group:
            return _("Quota for %s") % str(obj.group)
        return _('Quota for Everyone')

    def quota_size(self, obj):
        return filesizeformat(obj.size)

admin.site.register(Quota, QuotaAdmin)

