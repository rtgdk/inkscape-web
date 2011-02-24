from collections import namedtuple
from django.template.defaultfilters import slugify
from django.conf import settings
import datetime
from django.utils.safestring import mark_safe
from docutils.core import publish_parts
import os


class ParsedFile(object):
    """
    Simple parser for files or strings in the style of HTTP requests with a
    header block and body. Stores headers in items - self['Header-Name'] - and
    the body in self.body.
    """
    def __init__(self, file_name_or_handle):
        self._items = {}
        if isinstance(file_name_or_handle, basestring):
            handle = self.handle = open(file_name_or_handle, 'U')
        else:
            handle = self.handle = file_name_or_handle

        for line in handle:
            if line == '\n':
                break
            try:
                key, value = line.rstrip('\n').split(': ')
            except ValueError:
                raise ValueError('Invalid file format.')
            self[key] = value
        else:
            raise ValueError('Invalid file format.')

        self.body = ''
        for line in handle:
            self.body += line
        #self.body = ''.join(handle.readlines())

    def __setitem__(self, item, value):
        self._items[item] = value

    def __getitem__(self, item):
        return self._items[item]

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default


def load_article(language, year, slug):
    """Load an article to an Article object."""

    return Article.from_parsedfile(ParsedFile(os.path.join(settings.NEWS_PATH,
        language, year, slug + '.rst')), slug)


class Article(namedtuple('Article', 'title author date slug category body')):
    __slots__ = ()

    @classmethod
    def from_parsedfile(cls, article, slug):
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

    @property
    def category_url(self):
        return '/news/category/%s/' % slugify(self.category)

    @property
    def author_url(self):
        return '/users/%s/' % slugify(self.author)
