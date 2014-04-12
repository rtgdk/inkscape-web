from __future__ import absolute_import

from django import forms
from django.conf import settings
from django.contrib.admin import widgets  

from cms.plugin_pool import plugin_pool
from cms.plugins.text.settings import USE_TINYMCE

from .widgets.wymeditor_widget import WYMEditor
from .models import News

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        exclude = ('creator', 'editor', 'created', 'updated', 'language', 'translation_of')
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

    def _get_widget(self):
        plugins = plugin_pool.get_text_enabled_plugins(placeholder=None,
                page=None)
        if USE_TINYMCE and "tinymce" in settings.INSTALLED_APPS:
            from cmsplugin_news.widgets.tinymce_widget import TinyMCEEditor
            return TinyMCEEditor(installed_plugins=plugins)
        else:
            return WYMEditor(installed_plugins=plugins)

    def __init__(self, *args, **kwargs):
        super(NewsAdminForm, self).__init__(*args, **kwargs)
        widget = self._get_widget()
        self.fields['excerpt'].widget = widget
        self.fields['content'].widget = widget
        self.fields['translation_of'].queryset = News.objects.filter(language="")

