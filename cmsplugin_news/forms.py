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
"""
Provide the admin with a editing interface including Html fields.
"""

from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.conf import settings
from django.contrib.admin import widgets

from cms.plugin_pool import plugin_pool
from djangocms_text_ckeditor.widgets import TextEditorWidget

from .models import News

class NewsAdminForm(ModelForm):
    english = News.objects.filter(language="")

    class Meta:
        model = News
        exclude = ('creator', 'editor', 'created', 'updated', 'language',
                   'translation_of', 'pub_date')

    class Media:
        css = {'all': ('css/admin.news.css',)}
        js = ('admin/js/collapse.js',)

    def __init__(self, *args, **kwargs):
        super(NewsAdminForm, self).__init__(*args, **kwargs)

        if 'translation_of' in self.fields:
            self.fields['translation_of'].queryset = self.english

        kw = dict(configuration='CKEDITOR_NEWS')
        if 'excerpt' in self.fields:
            self.fields['excerpt'].widget = TextEditorWidget(**kw)

        if 'content' in self.fields:
            self.fields['content'].widget = TextEditorWidget(**kw)


class TranslationForm(NewsAdminForm):
    template = "<fieldset class='tr collapse close'>"\
               "<h2>%s</h2>%%s</fieldset>" % _('English Version')

    def __init__(self, language, *args, **kwargs):

        self.language = language
        if kwargs['instance'].translation_of:
            self.translation_of = kwargs['instance'].translation_of
        else:
            self.translation_of = kwargs['instance']
            kwargs['instance'], _ = News.objects.get_or_create(
                language=language, translation_of=self.translation_of,
                defaults={
                    'title': self.translation_of.title,
                    'link': self.translation_of.link,
                    'excerpt': self.translation_of.excerpt,
                    'content': self.translation_of.content,
                })

        super(TranslationForm, self).__init__(*args, **kwargs)

        # Set the help texts to the English version
        for key in ('excerpt', 'content'):
            attrs = {'id': 't_%s' % key}
            content = getattr(self.translation_of, key)
            editor = TextEditorWidget(configuration='CKEDITOR_READONLY')
            text = editor.render(attrs['id'], content, attrs)
            self.fields[key].help_text = self.template % text

