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

from django.forms import *
from django.contrib.admin import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission

from ajax_select import make_ajax_field, make_ajax_form
from ajax_select.admin import AjaxSelectAdmin

# Add permission to admin so we can remove old stuff
class PermissionAdmin(ModelAdmin):
    list_display = ('name', 'content_type', 'codename')
    search_fields = ('name', 'codename')
    list_filter = ('content_type',)

site.register(Permission, PermissionAdmin)

from .models import *

class ChatRoomInline(TabularInline):
    model = TeamChatRoom
    # XXX admin field can not be added until Ajaxselect works
    fields = ('channel', 'language')

class TeamAdmin(AjaxSelectAdmin):
    form = make_ajax_form(Team, {'admin': 'user'}, show_help_text=True)
    list_display = ('name', 'group', 'admin', 'enrole')
    inlines = (ChatRoomInline,)
    readonly_fields = ('watchers', 'requests')

site.register(Team, TeamAdmin)


class UserAdmin(UserAdmin):
    search_fields = ('username', 'first_name', 'last_name', 'bio', 'ircnick')
    readonly_fields = ('photo_preview',)
    # We make a copy of the fieldsets from the UserAdmin class so we can
    # customise it without any compelxity. Copied from Django 1.8.
    fieldsets = ( 
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'language',
                              'bio', 'gpg_key', 'photo_preview', 'photo')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'), 'classes': ('collapse', 'close'),}),
        (_('Social Networks'), {'fields': ('ircnick', 'dauser', 'ocuser', 'tbruser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_seen', 'visits')}),
    ) 

site.register(User, UserAdmin)

