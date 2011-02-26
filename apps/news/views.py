from django.http import Http404, HttpResponseBadRequest
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils._os import safe_join
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
import os
import datetime
from docutils.core import publish_parts
from .datatypes import Article, ParsedFile
from ...nav import leaf


def archive_all(request):
    raise Http404('All news')


def archive_year(request, year):
    raise Http404('Annual news for %s' % year)


def article(request, year, slug):
    try:
        return _load_article(request, request.LANGUAGE_CODE,
                year, slug)
    except Http404:
        return _load_article(request, 'en', year, slug,
        # Translators: replace "the current language" with the language name
                mark_safe(_('This page is not available in English. Here is '
                    'the English version of this page. If you would like to '
                    'help with translating this website, please '
                    '<a href="">contact us</a>.')))


def _load_article(request, language, year, slug, message=None):
    url = '%s/%s' % (year, slug)
    year = int(year)
    try:
        full_path = safe_join(os.path.abspath(os.path.join(
            settings.NEWS_PATH, language)), url) + '.rst'
    except ValueError:  # They've tried something like ../
        return HttpResponseBadRequest("No cheating.")

    if os.path.exists(full_path):
        if message:
            messages.info(request, message)
        article = ParsedFile(full_path)
        title = article['Title']
        author = article['Author']
        category = article['Category']
        try:
            date = datetime.date(*map(int, article['Date'].split('-')))
        except (ValueError, TypeError):
            raise ValueError('Invalid date %r in %r (should be yyyy-mm-dd)' % (article['Date'], full_path))

        parts = publish_parts(source=article.body,
                settings_overrides=getattr(settings, 'RST_SETTINGS_OVERRIDES',
                    {}),
                writer_name='html')

        article = Article(title, author, date, slug, category,
                mark_safe(parts['body']))
        return direct_to_template(request, 'news_full.html', {
            'title': title,
            'article': article,
            'breadcrumb_override': ((leaf(_('News'), '/news/'),
        leaf(year, '/news/%s/' % year)), leaf(title, ''))
            })
    else:
        raise Http404('No content at %r' % full_path)

def category(request, slug):
    raise Http404('Unable to do this yet.')
