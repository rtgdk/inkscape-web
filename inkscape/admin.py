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

from .models import ErrorLog, HeartBeat
from .templatetags.inkscape import timetag_filter

BOLD = "<strong style='display: block; width: 98%%; padding: 6px; color: white; background-color: %s;'>%s</strong>"

class ContentTypeAdmin(ModelAdmin):
    list_display = ('__str__', 'app_label', 'model', 'is_defunct')
    list_filter = ('app_label',)
    search_fields = ('model',)

    def is_defunct(self, obj):
        if not obj.model_class():
            return mark_safe(BOLD % ('red', 'DEFUNCT'))
        return "OK"

site.register(ContentType, ContentTypeAdmin)
site.register(ErrorLog)

class HeartBeatAdmin(ModelAdmin):
    list_display = ('name', 'started', 'last_ping', 'beats', 'status', 'in_error')

    def in_error(self, obj):
        if obj.status < 0:
            return mark_safe(BOLD % ('red', obj.error[:255]))
        if obj.error:
            if obj.status == 0:
                return mark_safe(BOLD % ('#080', obj.error[:255]))
            return mark_safe(BOLD % ('#aaa', obj.error[:255]))
        return "RUNNING"

    def started(self, obj):
        return timetag_filter(obj.created)

    def last_ping(self, obj):
        return timetag_filter(obj.updated)

site.register(HeartBeat, HeartBeatAdmin)

