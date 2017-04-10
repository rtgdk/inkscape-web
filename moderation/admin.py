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

from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import *

from ajax_select import make_ajax_field
from ajax_select.admin import AjaxSelectAdmin
from django.forms import ModelForm

from .models import FlagObject, FlagVote

class VoteForm(ModelForm):
    moderator = make_ajax_field(FlagVote, 'moderator', 'user', \
        help_text=_('Flagger or Moderator'))

class VoteInline(TabularInline):
    form = VoteForm
    model = FlagVote
    extra = 1 

class FlagForm(ModelForm):
    object_owner = make_ajax_field(FlagObject, 'object_owner', 'user')

class FlagAdmin(AjaxSelectAdmin):
    list_filter = ('resolution',)
    inlines = (VoteInline,)
    form = FlagForm

site.register(FlagObject, FlagAdmin)

