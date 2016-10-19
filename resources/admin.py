#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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

from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import *

from ajax_select import make_ajax_field
from ajax_select.admin import AjaxSelectAdmin

from .forms import ModelForm
from .models import *

class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'filterable', 'item_count')
    list_filter = ('filterable',)
    search_fields = ('name',)

    def item_count(self, obj):
        return obj.items.count()

site.register(License, CategoryAdmin)
site.register(Category, CategoryAdmin)

class ResourceForm(ModelForm):
    user = make_ajax_field(Resource, 'user', 'user', \
        help_text=_('Select Resource\'s Owner'))
    checked_by = make_ajax_field(Resource, 'checked_by', 'user', \
        help_text=_('Resource has been checked by this user'))

class ResourceAdmin(ModelAdmin):
    list_display = ('name', 'user', 'category', 'gallery')
    list_filter = ('published', 'category')
    search_fields = ('name', 'user__username', 'galleries__name')
    readonly_fields = ('slug','liked','viewed','downed','fullview')
    form = ResourceForm

site.register(Resource, ResourceAdmin)
site.register(ResourceMirror)
site.register(Vote)
site.register(TagCategory)

class TagAdmin(ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

site.register(Tag, TagAdmin)

class QuotaAdmin(ModelAdmin):
    list_display = ('name', 'quota_size')

    def name(self, obj):
        if obj.group:
            return _("Quota for %s") % str(obj.group)
        return _('Quota for Everyone')

    def quota_size(self, obj):
        return filesizeformat(obj.size * 1024)

site.register(Quota, QuotaAdmin)

class GalleryForm(ModelForm):
    user  = make_ajax_field(Gallery, 'user', 'user', \
        help_text=_('Select Group\'s Owner'))

class GalleryAdmin(ModelAdmin):
    readonly_fields = ('items', 'slug')
    list_display = ('name', 'user', 'group', 'status', 'item_count')
    list_filter = ('group', 'status')
    search_fields = ('name', 'user')
    form = GalleryForm

    def item_count(self, obj):
        return obj.items.count()

site.register(Gallery, GalleryAdmin)
