from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.utils.encoding import force_text

to_unicode = lambda s: force_text(s, strings_only=True)

from . import models
from . import settings

class NewsFeed(Feed):
    title = settings.FEED_TITLE
    description = settings.FEED_DESCRIPTION

    title_template = 'news/feeds/item_title.html'
    description_template = 'news/feeds/item_description.html'

    @property
    def link(self):
        return reverse('news_archive_index')

    def items(self):
        models.News.published.select_language(get_language())
        return models.News.published.all()[:settings.FEED_SIZE]

    def get_feed(self, *args, **kwargs):
        feed = Feed.get_feed(self, *args, **kwargs)
        # Force the language in the feed to be correct (bad design django Feed!)
        feed.feed['language'] = to_unicode(get_language())
        return feed

    def item_url(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.pub_date
