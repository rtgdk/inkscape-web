#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
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

from django.contrib.admin import *
from django.forms import ModelForm

from .models import *

class PlatformInline(StackedInline):
    model = ReleasePlatform
    extra = 1
    #readonly_fields = ('created',)
    #list_display = ('title', 'manager', 'started')

class ReleaseAdmin(ModelAdmin):
    inlines = (PlatformInline,)

class PlatformForm(ModelForm):

    def __init__(self, *args, **kwargs):
        ModelForm.__init__(self, *args, **kwargs)
        
        if self.instance.pk is not None and 'parent' in self.fields:
            non_parents = [ p.pk for p in self.instance.descendants() ] + [self.instance.pk]
            self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(pk__in=non_parents)

class PlatformAdmin(ModelAdmin):
    form = PlatformForm

site.register(Release, ReleaseAdmin)
site.register(Platform, PlatformAdmin)
site.register(ReleasePlatform)
