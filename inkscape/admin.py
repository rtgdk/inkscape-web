#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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

from django.utils.safestring import mark_safe

from django.contrib.admin import ModelAdmin, site
from django.contrib.contenttypes.models import ContentType

class ContentTypeAdmin(ModelAdmin):
    list_display = ('__str__', 'app_label', 'model', 'is_defunct')
    list_filter = ('app_label',)
    search_fields = ('model',)

    def is_defunct(self, obj):
        if obj.model_class():
            return mark_safe("<strong style='display: block; width: 100%; padding: 6px; color: white; background-color: red;'>DEFUNCT</strong>")
        return "OK"

site.register(ContentType, ContentTypeAdmin)

