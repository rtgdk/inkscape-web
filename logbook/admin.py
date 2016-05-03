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

from django.contrib.admin import *

from .models import *

class FileAdmin(ModelAdmin):
    model = LogFile
    list_display = ('filename', 'touched', 'inode')
    readonly_fields = ('filename', 'touched', 'inode')

site.register(LogFile)


site.register(LogMetric)

class NameAdmin(ModelAdmin):
    model = LogName
    list_display = ('re_family', 're_name', 'family', 'name')
    list_filter = ('re_family', 'family')
    readonly_fields = ('family', 'name')
    search_fields = ['name', 're_name']

site.register(LogName, NameAdmin)

