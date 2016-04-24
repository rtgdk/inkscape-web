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

"""
Tests for the cmsplugin_news app
"""

from django.utils import timezone
from datetime import timedelta

from django.test import TestCase

from cmsplugin_news.models import News

from django.contrib.auth import get_user_model
from . import settings as news_settings

class NewsTest(TestCase):
    urls = 'cmsplugin_news.urls'

    def setUp(self):
        self.today = timezone.now()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.user = get_user_model()(username='testuser')
        self.user.save()
        News.published.select_language('en')

    def tearDown(self):
        pass

    def test_unpublished(self):
        """
            Test if unpublished items are hidden by default
        """
        unpublished = News.objects.create(
            title='Unpublished News',
            slug='unpublished-news',
            is_published=False,
            pub_date=self.yesterday,
            creator=self.user,
        )
        self.assertEquals(News.published.count(), 0)
        unpublished.is_published = True
        unpublished.save()
        self.assertEquals(News.published.count(), 1)
        unpublished.is_published = False
        unpublished.save()
        self.assertEquals(News.published.count(), 0)
        unpublished.delete()

    def test_future_published(self):
        """
            Tests that items with a future published date are hidden
        """
        future_published = News.objects.create(
            title='Future published News',
            slug='future-published-news',
            is_published=True,
            pub_date=self.tomorrow,
            creator=self.user,
        )
        self.assertEquals(News.published.count(), 0)
        future_published.pub_date = self.yesterday
        future_published.save()
        self.assertEquals(News.published.count(), 1)
        future_published.pub_date = self.tomorrow
        future_published.save()
        self.assertEquals(News.published.count(), 0)

    def _test_language(self):
        """Test translations of articles"""
        item = News.objects.create(
            title='Original Language',
            slug='news',
            is_published=True,
            pub_date=self.yesterday,
            creator=self.user,
        )
        item.save()
        self.assertEqual(item.language, '')
        self.assertEqual(News.published.count(), 1)

        trans = News.objects.create(
            title='Translation',
            slug='news',
            is_published=True,
            pub_date=self.yesterday,
            creator=self.user,
            translation_of=item,
            language='fr',
        )
        trans.save()
        self.assertEqual(trans.language, 'fr')
        self.assertEqual(News.published.count(), 1)
        
        self.assertEqual(item.translations.count(), 1)
        self.assertEqual(item.translations.all()[0], trans)
        self.assertEqual(item.title, 'Original Language')
        self.assertEqual(trans.is_original(), True)
        self.assertEqual(item.is_original(), True)

        item.select_language('fr')
        self.assertEqual(item.title, 'Translation')
        self.assertEqual(item.is_original(), False)
        self.assertEqual(trans.is_original(), True)

    def test_navigation(self):
        """
            Tests if the navigation build by navigation.get_nodes is correct
        """
        pass

    def test_link_as_url_without_content(self):
        """
        If the news item contains a link but no content and
        USE_LINK_ON_EMPTY_CONTENT_ONLY as well as LINK_AS_ABSOLUTE_URL are
        enabled use this link as absolute url for the item.
        """
        news_settings.USE_LINK_ON_EMPTY_CONTENT_ONLY = True
        news_settings.LINK_AS_ABSOLUTE_URL = True
        item = News.objects.create(
            title='Future published News',
            slug='future-published-news',
            is_published=True,
            pub_date=self.tomorrow,
            link='http://lala.com/',
            creator=self.user,
        )
        self.assertEquals('http://lala.com/', item.get_absolute_url())

    def test_link_as_url_with_content(self):
        """
        Same as above, but this time the news item actually has a content
        and should therefor not use the provided link.
        """
        news_settings.USE_LINK_ON_EMPTY_CONTENT_ONLY = True
        news_settings.LINK_AS_ABSOLUTE_URL = True
        item = News.objects.create(
            title='Future published News',
            slug='future-published-news',
            content='test',
            is_published=True,
            pub_date=self.tomorrow,
            link='http://lala.com/',
            creator=self.user,
        )
        # XXX This get_absolute_url fails because the url namespaces aren't loaded
        # yet and I wonder if this is something to do with testing urls.
        self.assertNotEquals('http://lala.com/', item.get_absolute_url())



