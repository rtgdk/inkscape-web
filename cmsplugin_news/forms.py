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

