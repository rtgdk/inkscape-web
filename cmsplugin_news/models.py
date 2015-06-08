from django.utils import timezone

from django.db.models import *
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from cms.utils.permissions import get_current_user as get_user
from cms.models import CMSPlugin

from . import settings

import sys
import inspect

class LanguageNotSet(Exception):
    pass

class LanguageQuerySet(QuerySet):
    def select_language(self, lang):
        self.language = lang
        return self

    def _clone(self, *args, **kwargs):
        qs = super(LanguageQuerySet, self)._clone(*args, **kwargs)
        if hasattr(qs, 'select_language'):
            qs.select_language(self.language)
        return qs

    def iterator(self):
        if not hasattr(self, 'language'):
            raise LanguageNotSet("Can't iterate over news before the language is selected (%s)." % id(self))
        for result in super(LanguageQuerySet, self).iterator():
            yield result.select_language(self.language)


class PublishedManager(Manager):
    """This manager allows filtering of published vs not-published as well as language
       selection at display time."""
    def select_language(self, lang):
        self.language = lang
        return self

    def get_queryset(self):
        if not hasattr(self, 'language'):
            raise LanguageNotSet("Can't do a language dependant query before the language is selected.")
        return LanguageQuerySet(self.model, using=self._db).select_language(self.language)\
                .filter(is_published=True, pub_date__lte=timezone.now(), translation_of__isnull=True)


class News(Model):
    title        = CharField(_('Title'), max_length=255)
    slug         = SlugField(_('Slug'), unique_for_date='pub_date', blank=True, null=True,
                     help_text=_('A slug is a short name which uniquely identifies the news item.'))
    excerpt      = TextField(_('Excerpt'), blank=True)
    content      = TextField(_('Content'), blank=True)

    is_published = BooleanField(_('Published'), default=False)
    pub_date     = DateTimeField(_('Publication date'), default=timezone.now)

    created      = DateTimeField(auto_now_add=True, editable=False)
    updated      = DateTimeField(auto_now=True, editable=False)

    creator      = ForeignKey(User, related_name="created_news", default=get_user)
    editor       = ForeignKey(User, blank=True, null=True, related_name="edited_news")

    link         = URLField(_('Link'), blank=True, null=True,
                     help_text=_('This link will be used a absolute url for this item and replaces'
                                 ' the view logic. <br />Note that by default this only applies for'
                                 ' items with an empty "content" field.'))

    # The translation functionality could be brought into a more generic format
    # By making a meta class which doesn't have it's own table but contains these two fields
    # and specifying 1. a list of translated fields which __getattr always passes UP to the
    # translated version and 2. a list of base fields which __getattr always passes DOWN to the root.
    # All mechanisms to do with translations would then be brought into that generic class.
    language     = CharField(_("Language"), max_length=5, choices=settings.OTHER_LANGS,
                     help_text=_("Translated version of another news item."))
    translation_of = ForeignKey("self", blank=True, null=True, related_name="translations")

    # django uses the first object manager for reverse lookups. Make sure normal manager is first.
    objects   = Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ('-pub_date', )
        permissions = (
            ('translate', _('Translate News')),
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
        if hasattr(self, 'trans') and name in ['translated','title','excerpt','language','content']:
            obj = self.trans
        elif name == 'translated':
            name = 'updated'
        return Model.__getattribute__(obj, name)

    def get_translations(self):
        if self.translation_of:
            return self.translation_of.get_translations()
        return self.translations.all()

    def get_translation(self, lang):
        for item in self.get_translations():
            if item.language == lang:
                return item
        return None

    def needs_translation(self):
        return not self.is_original() and (self.trans == self or self.trans.updated < self.updated)

    def is_original(self):
        return not hasattr(self, '_lang') or self._lang == settings.DEFAULT_LANG

    def get_absolute_url(self):
        if settings.LINK_AS_ABSOLUTE_URL and self.link:
            if settings.USE_LINK_ON_EMPTY_CONTENT_ONLY and not self.content:
                return self.link
        if self.is_published and self.slug:
            return reverse('news_detail', kwargs={
                'year'  : self.pub_date.strftime("%Y"),
                'month' : self.pub_date.strftime("%m"),
                'day'   : self.pub_date.strftime("%d"),
                'slug'  : self.slug})
        return reverse('news_item', kwargs={ 'news_id': self.id })


class LatestNewsPlugin(CMSPlugin):
    """
        Model for the settings when using the latest news cms plugin
    """
    limit = PositiveIntegerField(_('Number of news items to show'),
                    help_text=_('Limits the number of items that will be displayed'))


