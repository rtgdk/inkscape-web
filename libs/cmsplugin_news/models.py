from django.utils import timezone

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User

from cms.models import CMSPlugin

from . import settings


class PublishedNewsManager(models.Manager):
    """
        Filters out all unpublished and items with a publication date in the future
    """
    def get_query_set(self):
        return super(PublishedNewsManager, self).get_query_set() \
                    .filter(is_published=True) \
                    .filter(pub_date__lte=timezone.now())

class News(models.Model):
    """
    News
    """

    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'), unique_for_date='pub_date',
                        help_text=_('A slug is a short name which uniquely identifies the news item for this day'))
    excerpt = models.TextField(_('Excerpt'), blank=True)
    content = models.TextField(_('Content'), blank=True)

    is_published = models.BooleanField(_('Published'), default=False)
    pub_date     = models.DateTimeField(_('Publication date'), default=timezone.now)

    created      = models.DateTimeField(auto_now_add=True, editable=False)
    updated      = models.DateTimeField(auto_now=True, editable=False)

    creator      = models.ForeignKey(User, related_name="created_news")
    editor       = models.ForeignKey(User, blank=True, null=True, related_name="edited_news")

    translation_of = models.ForeignKey("News", blank=True, null=True, related_name="translations")
    language = models.CharField(_("Language"), max_length=5, choices=LANGUAGES, help_text=_("Optional: Show only for this language"))
    link     = models.URLField(_('Link'), blank=True, null=True, help_text=_('This link will be used a absolute url'
                  ' for this item and replaces the view logic. <br />Note that by'
                  ' default this only applies for items with an empty "content"'
                  ' field.'))

    published = PublishedNewsManager()
    objects   = models.Manager()

    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ('-pub_date', )

    def __unicode__(self):
        return self.title

    def is_visible(self):
        return self.is_published and self.pub_date < timezone.now()

    def get_absolute_url(self):
        if settings.LINK_AS_ABSOLUTE_URL and self.link:
            if settings.USE_LINK_ON_EMPTY_CONTENT_ONLY and not self.content:
                return self.link
        if self.is_visible():
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
    limit = models.PositiveIntegerField(_('Number of news items to show'),
                    help_text=_('Limits the number of items that will be displayed'))

