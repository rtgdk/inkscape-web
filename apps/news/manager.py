"""
A module for managing news articles (essentially replacing a database).
"""

from collections import namedtuple
from django.conf import settings
import datetime
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from docutils.core import publish_parts
import os
from ...httpfileformat import HttpFormatFile
from collections import defaultdict


def load_article(language, year, slug):
    """Load an article to an Article object."""

    return Article.from_file(HttpFormatFile(
        os.path.join(settings.NEWS_PATH, language, str(year), slug + '.rst')),
        slug)


class Article(namedtuple('Article', 'title author date slug category body')):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)

    @classmethod
    def from_file(cls, article, slug):
        title = article['Title']
        author = article['Author']
        category = article['Category']
        try:
            date = datetime.date(*map(int, article['Date'].split('-')))
        except (ValueError, TypeError):
            raise ValueError('Invalid date %r (should be yyyy-mm-dd)'
                    % article['Date'])

        parts = publish_parts(source=article.body,
                settings_overrides=getattr(settings, 'RST_SETTINGS_OVERRIDES',
                    {}),
                writer_name='html')

        article = cls(title, author, date, slug, category,
                mark_safe(parts['body']))

        return article

    @property
    def brief(self):
        return mark_safe(''.join(self.body.partition('</p>')[0:2]))


class _NewsManager(object):
    """
    A manager for news articles. This keeps track of categories, dates with
    posts, and more. It updates its catalogue via the ``update`` method.

    self.categories is a list of two-tuples, ('Category name', article_count),
    sorted by article count then lexicographic category name.

    """

    def __init__(self):
        self.update()

    def update(self):
        """
        Architectural note:

        self.articles_by_year[year][slug][language] is an Article
        self.articles_by_category[cat_slug][year, slug][language] is an Article
        """

        articles = defaultdict(dict)
        by_year = defaultdict(lambda: defaultdict(dict))
        by_cat = defaultdict(lambda: defaultdict(dict))
        catmap = {}

        for language in os.listdir(settings.NEWS_PATH):
            language_path = os.path.join(settings.NEWS_PATH, language)
            if not os.path.isdir(language_path):
                continue
            for year in os.listdir(language_path):
                try:
                    year = int(year)
                except TypeError:
                    continue  # This shouldn't ever happen, but don't die
                year_path = os.path.join(language_path, str(year))
                if not os.path.isdir(year_path):
                    continue
                for slug in os.listdir(year_path):
                    if not slug.endswith('.rst'):
                        continue  # This shouldn't ever happen, but don't die
                    slug = slug[:-4]  # Trim .rst
                    article = load_article(language, year, slug)
                    articles[year, slug][language] = article
                    by_year[year][slug][language] = article
                    by_cat[article.category][year, slug][language] = \
                            article
                    catmap[slugify(article.category)] = article.category

        # We only update ``self.*`` at the end, so that it can be used in other
        # threads with the old catalogue until the new one is ready.
        articles = articles.values()
        articles.sort(key=lambda x: x['en'].date, reverse=True)
        self.articles = articles
        self.articles_by_year = by_year
        self.articles_by_category = by_cat
        self.category_slugs = catmap

        self.categories = [(cat, len(articles))
                    for cat, articles in self.articles_by_category.iteritems()]
        self.categories.sort(key=lambda x: x[0])  # sort by category name
        self.categories.sort(key=lambda x: x[1])  # sort by frequency

    def get_article(self, year, slug, language, fallback_lang='en'):
        """
        Retrieves an Article by year, slug and language. If the article is not
        found in the specified language, but it is found in the fallback
        language ('en' by default), that latter will be selected.

        Returns a two-tuple of an ``Article`` and whether the language match is
        correct (``True``) or the fallback has been served instead (``False``).

        This is mainly a convenience method, removing the need to do a check
        for the current language and then for English.
        """
        year = int(year)
        y = self.articles_by_year[year]
        if not len(y):
            raise KeyError('No articles in year %r' % year)

        s = y[slug]
        if not len(s):
            raise KeyError('No article with slug %r in year %r' % (slug, year))

        if language in s:
            return s[language], True
        elif fallback_lang in s:
            return s[fallback_lang], False
        else:
            raise KeyError('Article %r from year %r not available in %r or %r'
                    % (slug, year, language, fallback_lang))

news_manager = _NewsManager()
