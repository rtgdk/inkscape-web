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

from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.contrib.admin import site, ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .models import *

class TeamAdmin(ModelAdmin):
    readonly_fields = ('watchers', 'requests')

site.register(Team, TeamAdmin)


class UserAdmin(UserAdmin):
    readonly_fields = ('photo_preview',)
    # We make a copy of the fieldsets from the UserAdmin class so we can
    # customise it without any compelxity. Copied from Django 1.8.
    fieldsets = ( 
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'language',
                              'bio', 'gpg_key', 'photo_preview', 'photo')}),
        (_('Social Networks'), {'fields': ('ircnick', 'ircdev', 'dauser', 'ocuser', 'tbruser')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_seen', 'visits')}),
    ) 

site.register(User, UserAdmin)

