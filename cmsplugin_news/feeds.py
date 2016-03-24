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

    title_template = 'cmsplugin_news/feeds/item_title.html'
    description_template = 'cmsplugin_news/feeds/item_description.html'

    @property
    def link(self):
        return reverse('news:archive_index')

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
