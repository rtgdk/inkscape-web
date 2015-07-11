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

from __future__ import absolute_import

from django import forms
from django.conf import settings
from django.contrib.admin import widgets  

from cms.plugin_pool import plugin_pool

from .models import News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('creator', 'editor', 'created', 'updated', 'language', 'translation_of','slug')
    def __init__(self, *args, **kwargs):
        super(NewsForm, self).__init__(*args, **kwargs)
        self.fields['pub_date'].widget = widgets.AdminSplitDateTime()

class NewsTranslationForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('creator', 'editor', 'created', 'updated', 'language', 'translation_of', 'pub_date')


class NewsAdminForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('creator', 'editor', 'created', 'updated')

    def __init__(self, *args, **kwargs):
        super(NewsAdminForm, self).__init__(*args, **kwargs)
        self.fields['translation_of'].queryset = News.objects.filter(language="")

