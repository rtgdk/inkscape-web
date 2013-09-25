
import os
import datetime

from . import settings
from . import processors

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


B_TYPES = (
  ('rss', 'RSS Feed'),
  #('html', 'HTML Scrape'),
)


class Brochure(models.Model):
    name    = models.CharField(_('Title'), max_length=82)
    desc    = models.TextField(_('Description'), null=True, blank=True)
    link    = models.URLField(_('Link to Full Listing'), null=True, blank=True)
    icon    = models.ImageField(_('Target Icon'),
        upload_to=os.path.join(settings.MEDIA_ROOT, 'icons'))

    kind    = models.CharField(_('Source Type'), max_length=4,
        choices=B_TYPES, default='rss', help_text=_('Kind of parsing to do.'))
    rss     = models.URLField(_('Data Link'), null=True, blank=True,
        help_text=_('Link to RSS feed or other data for regular parsing.'))
    publish = DateTimeField(_('Last Updated'), null=True, blank=True)

    is_published = models.BooleanField(_('Published'), default=True)

    def refresh(self):
        """Fill the brochure will new information"""
        if self.kind = 'rss':
            processors.rss(self)



class BrochureItem(models.Model):
    group   = models.ForeignKey(Brochure)
    title   = models.CharField(_('Title'), max_length=82)
    text    = models.CharField(_('Subtitle'), max_length=255)
    link    = models.URLField(_('Link'))
    publish = models.DateTimeField(_('Publication Date'), null=True)
    thumb   = models.ImageField(_('Thumbnail'),
        upload_to=os.path.join(settings.MEDIA_ROOT, 'icons'))

    enabled = models.BooleanField(_('Enabled'), default=True)
    indexed = models.DateTimeField(_('Indexed Date'), default=datetime.datetime.now)

    class Meta:
        ordering = ('-indexed', )

    def __unicode__(self):
        return self.title


class BrochurePlugin(CMSPlugin):
    limit  = models.PositiveIntegerField(_('Number of items'))
    source = models.ForeignKey(Brochure, null=True, blank=True)


