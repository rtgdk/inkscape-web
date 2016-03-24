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

from django.utils import timezone

from django.db.models import *
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf import settings
from .settings import OTHER_LANGS, DEFAULT_LANG, \
    LINK_AS_ABSOLUTE_URL, USE_LINK_ON_EMPTY_CONTENT_ONLY

from cms.utils.permissions import get_current_user as get_user
from cms.models import CMSPlugin

import sys
import inspect

class LanguageNotSet(Exception):
    pass


class PublishedManager(Manager):
    """This manager allows filtering of published vs not-published as well as language
       selection at display time."""
    def select_language(self, lang):
        self.language = lang
        return self

    def with_language(self, lang, **kwargs):
        return self.select_language(lang).get_queryset(**kwargs)

    def get_queryset(self, is_staff=False):
        if not hasattr(self, 'language'):
            raise LanguageNotSet("Can't do a language dependant query before the language is selected.")

        qs = super(PublishedManager, self).get_queryset()
        english = qs.filter(translation_of__isnull=True)

        if self.language == 'en':
            qs = english
        else:
            untranslated = english.exclude(translations__language=self.language)
            qs = untranslated | qs.filter(language=self.language)
        if not is_staff:
            qs = qs.filter(is_published=True, pub_date__lte=timezone.now())
        return qs


class News(Model):
    title = CharField(_('Title'), max_length=255)
    slug = SlugField(_('Slug'), unique_for_date='pub_date', null=True,
           help_text=_('A slug is a short name which provides a unique url.'))

    excerpt = TextField(_('Excerpt'), blank=True)
    content = TextField(_('Content'), blank=True)

    is_published = BooleanField(_('Published'), default=False)
    pub_date = DateTimeField(_('Publication date'), default=timezone.now)

    created = DateTimeField(auto_now_add=True, editable=False)
    updated = DateTimeField(auto_now=True, editable=False)

    creator = ForeignKey(settings.AUTH_USER_MODEL, related_name="created_news", default=get_user)
    editor  = ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="edited_news")

    link = URLField(_('Link'), blank=True, null=True,
         help_text=_('This link will be used as absolute url for this item '
           'and replaces the view logic. <br />Note that by default this '
           'only applies for items with an empty "content" field.'))

    # The translation functionality could be brought into a more generic format
    # By making a meta class which doesn't have it's own table but contains
    # these two fields and specifying 1. a list of translated fields which
    # __getattr always passes UP to the translated version and 2. a list of
    # base fields which __getattr always passes DOWN to the root.
    # All mechanisms to do with translations would then be brought into
    # that generic class.
    language     = CharField(_("Language"), max_length=8, choices=OTHER_LANGS, db_index=True,
                     help_text=_("Translated version of another news item."))
    translation_of = ForeignKey("self", blank=True, null=True, related_name="translations")

    # django uses the first object manager for reverse lookups.
    # Make sure normal manager is first.
    objects   = Manager()
    published = PublishedManager()

    tr_fields = ['translated', 'title', 'excerpt', 'language', 'content']

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ('-pub_date', )
        permissions = (
            ('translate_news', _('Translate News')),
        )

    @property
    def lang(self):
        return self.language or 'en'

    def __unicode__(self):
        return self.title

    def select_language(self, lang):
        self._lang = lang.split('-')[0]
        self.trans = self.get_translation(lang) or self
        return self

    def __getattribute__(self, name):
        obj = self
        if hasattr(self, 'trans') and name in self.tr_fields:
            obj = self.trans
        elif name == 'translated':
            name = 'updated'
        return Model.__getattribute__(obj, name)

    def get_translations(self):
        if self.translation_of:
            return self.translation_of.get_translations()
        return self.translations.all()

    def get_translation(self, lang):
        try:
            return self.get_translations().get(language=lang)
        except News.DoesNotExist:
            return None

    def needs_translation(self):
        return not self.is_original() and (self.trans == self or self.trans.updated < self.updated)

    def is_original(self):
        return not hasattr(self, '_lang') or self._lang == DEFAULT_LANG

    def save(self, **kw):
        """Keep translations fields up to date with master english version"""
        if self.translation_of:
            self.is_published = self.translation_of.is_published
            self.pub_date = self.translation_of.pub_date
        else:
            self.translations.update(
              is_published=self.is_published,
              pub_date=self.pub_date)
        return super(News, self).save(**kw)

    @classmethod
    def get_list_url(cls):
        return reverse('news:archive_index')

    def get_absolute_url(self):
        if LINK_AS_ABSOLUTE_URL and self.link:
            if USE_LINK_ON_EMPTY_CONTENT_ONLY and not self.content:
                return self.link
        if self.is_published and self.slug:
            return reverse('news:detail', kwargs={
                'year'  : self.pub_date.strftime("%Y"),
                'month' : self.pub_date.strftime("%m"),
                'day'   : self.pub_date.strftime("%d"),
                'slug'  : self.slug})
        return reverse('news:item', kwargs={'pk': self.pk})


class LatestNewsPlugin(CMSPlugin):
    """
        Model for the settings when using the latest news cms plugin
    """
    limit = PositiveIntegerField(_('Number of news items to show'),
                    help_text=_('Limits the number of items that will be displayed'))

