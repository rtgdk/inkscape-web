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

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext
from django.contrib.admin import site, ModelAdmin
from django.contrib.auth import get_permission_codename

from cms.utils import get_language_from_request as get_lang
from cmsplugin_news.forms import NewsAdminForm, TranslationForm
from cmsplugin_news.models import News

class NewsAdmin(ModelAdmin):
    """Admin for news"""
    date_hierarchy = 'pub_date'
    list_display = ('title', 'language', 'translation_of', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'language')
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    form = NewsAdminForm

    actions = ['make_published', 'make_unpublished']
    fieldsets = (
       (_('Info'), {'fields': ('title', 'slug', 'link')}),
       (_('Actual Content'), {'fields': ('excerpt', 'content')})
    )

    save_as = True
    save_on_top = True

    def get_urls(self):
        from django.conf.urls import url
        urls = super(NewsAdmin, self).get_urls()
        wrap = self.admin_site.admin_view
        opts = self.model._meta
        info = opts.app_label, opts.model_name,

        return [
          url(r'^(.+)/tr/$', wrap(self.tr_view), name='%s_%s_translate' % info),
        ] + urls

    def get_form(self, request, obj, fields=None):
        """Returns a different form if we are translating"""
        form = super(NewsAdmin, self).get_form(request, obj, fields=fields)

        class _Form(TranslationForm):
            def __init__(self, *args, **kwargs):
                super(_Form, self).__init__(get_lang(request), *args, **kwargs)

        if request.resolver_match.url_name.endswith('_translate'):
            return _Form
        return form

    def tr_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = {'translation': True}
        return self.changeform_view(request, object_id, form_url, extra_context)

    def has_change_permission(self, request, obj=None):
        if request.resolver_match.url_name.endswith('_translate'):
            opts = self.opts
            codename = get_permission_codename('translate', opts)
            return request.user.has_perm("%s.%s" % (opts.app_label, codename))
        return super(NewsAdmin, self).has_change_permission(request, obj)

    def get_queryset(self, request):
        """
            Override to use the objects and not just the default visibles only.
        """
        return News.objects.all()

    def make_published(self, request, queryset):
        """
            Marks selected news items as published
        """
        rows_updated = queryset.update(is_published=True)
        self.message_user(request,
            ungettext('%(count)d newsitem was published',
                      '%(count)d newsitems were published',
                      rows_updated) % {'count': rows_updated})
    make_published.short_description = _('Publish selected news')

    def make_unpublished(self, request, queryset):
        """
            Marks selected news items as unpublished
        """
        rows_updated = queryset.update(is_published=False)
        self.message_user(request,
            ungettext('%(count)d newsitem was unpublished',
                      '%(count)d newsitems were unpublished',
                      rows_updated) % {'count': rows_updated})
    make_unpublished.short_description = _('Unpublish selected news')

site.register(News, NewsAdmin)
