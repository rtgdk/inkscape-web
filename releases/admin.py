#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
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
from ajax_select.admin import AjaxSelectAdmin

from .forms import ReleaseForm, PlatformForm, TranslationInlineFormSet
from .models import *

class PlatformInline(StackedInline):
    model = ReleasePlatform
    extra = 1

class TranslationsInline(StackedInline):
    model = ReleaseTranslation
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        return TranslationInlineFormSet

class ReleaseAdmin(AjaxSelectAdmin):
    form = ReleaseForm
    inlines = (PlatformInline, TranslationsInline)
    list_display = ('version', 'parent', 'release_date', 'manager')

class PlatformAdmin(AjaxSelectAdmin):
    form = PlatformForm

site.register(Release, ReleaseAdmin)
site.register(Platform, PlatformAdmin)
site.register(ReleasePlatform)
