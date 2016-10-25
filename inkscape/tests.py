#
# Copyright 2016, Maren Hachmann <marenhachmann@yahoo.com>
#                 Martin Owens <doctormo@gmail.com>
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
Test breadcrumbs, caching keys and other core inkscape website functions.
"""

import os
import sys
import json

from django.contrib.auth.models import Permission, Group
from django.core.urlresolvers import reverse
from autotest.base import ExtraTestCase, MultipleFailureTestCase

from inkscape.middleware import AutoBreadcrumbMiddleware, TrackCacheMiddleware
from inkscape.url_utils import WebsiteUrls, UrlView
from inkscape.utils import QuerySetWrapper
from inkscape.models import ErrorLog

class WebsiteUrlTest(MultipleFailureTestCase):
    """Tests every page on the website"""
    credentials = {'username': 'admin', 'password': '123456'}
    fixtures = ['url_objects']

    @classmethod
    def setUpClass(cls):
        super(WebsiteUrlTest, cls).setUpClass()
        cls.url_bin = {}
        cls.url_file = os.path.join(cls.fixture_dir, 'url-bin.json')
        if os.path.isfile(cls.url_file):
            with open(cls.url_file) as fhl:
                cls.url_bin = json.loads(fhl.read())

    @classmethod
    def tearDownClass(cls):
        super(WebsiteUrlTest, cls).tearDownClass()
        if os.path.isdir(os.path.dirname(cls.url_file)):
            with open(cls.url_file, 'w') as fhl:
                fhl.write(json.dumps(cls.url_bin, indent=2, sort_keys=True))

    def assertBreadcrumbs(self, response, *terms):
        """Test the display of breadcrumbs"""
        crumbs = response.content.split('breadcrumbs">', 1)[-1].split('</div>')[0]
        try:
            for x, term in enumerate(terms):
                if len(term) == 1:
                    self.assertIn('<em class="crumb">%s<' % term, crumbs)
                elif x == len(terms) - 1 and len(terms) != 1:
                    self.assertIn('<em class="crumb">%s<' % term[1], crumbs)
                else:
                    self.assertIn('href="%s" class="crumb">%s<' % term, crumbs)
        except AssertionError:
            raise AssertionError("Breadcrumb %s missing from %s" % (unicode(term), crumbs))

    def assertBreadcrumbRequest(self, url, breadcrumbs, **kw):
        """Test a url for the right breadcrumbs"""
        self.assertBreadcrumbResponse(self.assertGet(url, **kw), breadcrumbs)

    def assertBreadcrumbResponse(self, response, breadcrumbs, empty=False, **kw):
        """Test a response contains the right breadcrumbs"""
        (LINKS, NAMES) = range(2)
        generated = response.context_data.get('breadcrumbs', [])
        result = zip(*generated) if generated else [(), ()]
        tester = zip(*breadcrumbs) if breadcrumbs else [(), ()]

        # The i18n gets in the way of testing the names
        result[NAMES] = tuple(unicode(item) for item in result[NAMES])
        tester[NAMES] = tuple(unicode(item) for item in tester[NAMES])

        if result[NAMES] and result[NAMES][0] == "Home":
            # We're going to assume Home is tested.
            result[NAMES] = result[NAMES][1:]
            result[LINKS] = result[LINKS][1:]

        self.assertTrue(empty or result[NAMES] or tester[NAMES],
            "No breadcrumbs to test and none provided, test should be skipped,"
            " flagged as empty or breadcrumbs added in the url json fixture.")

        self.assertListEqual(zip(*tester), zip(*result))

    def assertCacheKeyResponse(self, response, cache_keys, **kw):
        keys = list(getattr(response, 'cache_keys', []))
        try:
            self.assertListEqual(cache_keys, keys)
        except Exception as err:
            if False and raw_input("\n\nAre the keys [%s] correct for %s? [Y/N]: " % (", ".join(keys), kw.get('url', 'unknown'))) == 'Y':
                while cache_keys:
                    cache_keys.pop()
                cache_keys += keys
                return
            raise

    def assertContext(self, response, url):
        """Test context for the right objects"""
        if url.is_view:
            if url.url_type is UrlView.URL_DETAIL_TYPE:
                self.assertIn('object', response.context_data)
            elif url.url_type is UrlView.URL_LIST_TYPE:
                self.assertIn('object_list', response.context_data)
            elif url.url_type in (UrlView.URL_CREATE_TYPE, UrlView.URL_UPDATE_TYPE):
                self.assertIn('form', response.context_data)

    def test_all_urls(self):
        """Test every URL on the website

        The website urls test does a couple of things:

        1) Test each URL, making sure we get the right status
        2) Test the URL's breadcrumbs and links
        3) Test the response has object or object_list as expected (standard)
        4) Test objects have get_absolute_url which links correctly

        These are all done in one test to keep looping down.

        """
        self._limit = 5
        self._pad = 0
        skips = self.url_bin.get("skip", [])
        used_urls = set(["skip", "unneeded"])
        for url in WebsiteUrls():
            if url.slug not in self.url_bin and (
                  url.slug in skips \
                  or unicode(url.name) + "?*" in skips \
                  or unicode(url.namespace) + ":*" in skips):
                continue

            if not url.is_module:
                used_urls.add(url.slug)
                data = self.url_bin.setdefault(url.slug, {})
                if isinstance(data, dict):
                    data = [data]
                for datum in data:
                    self._pad -= 1
                    yield url.slug, self._test_url(url, datum)

        unneeded = list(used_urls & set(self.url_bin) ^ set(self.url_bin))
        try:
            if unneeded:
                self.url_bin['unneeded'] = unneeded
            else:
                self.url_bin.pop('unneeded', None)
            self.assertFalse(unneeded, "Extra urls found in url-bin (see unneeded)")
        except Exception as err:
            yield "extra_urls_in_bin", err

    def _test_url(self, url, datum):
        args = datum.get('args', [])
        kw = datum.get('kwargs', {})
        try:
            url_str = url.full_pattern
            self.assertThenSkip(self._limit <= 0, "Too many errors")
            self.assertThenSkip(self._pad > 0, "Skipping first")
            # We want to try and offer test writers some data to work with
            # in to url json file, so we parse the kwargs first.
            for key in list(url.kwargs):
                if key not in kw:
                    kw[key] = 'fill-me'
                    datum['kwargs'] = kw

            missing = []
            for key in list(kw):
                if key not in url.kwargs:
                    kw[key] = 'delete-me'
                    self.assertFalse(False, "Extra url kwarg found: %s" % key)
                if kw[key] == 'fill-me':
                    missing.append(key)

            self.assertFalse(missing, "Missing url kwarg(s): %s" % ', '.join(missing))

            url_str = url.test_url(*args, **kw)
            response = self.assertGet(url_str, status=datum.get('status', 200))

            if not hasattr(response, 'context_data'):
                raise ValueError("Response is not a TemplateResponse (should this be skipped?)")

            if datum.setdefault('breadcrumbs', []) is not None:
                self.assertBreadcrumbResponse(response, **datum)

            if datum.setdefault('cache_keys', []) is not None:
                datum['url'] = url.slug
                self.assertCacheKeyResponse(response, **datum)

            self.assertContext(response, url)
        except KeyError as err:
            raise
        except Exception as err:
            if self._pad <= 0:
                self._limit -= 1
            if err.args:
                err.args = (u"For url '%s' %s: %s" % (url.slug, url_str, err.args[0]),) + err.args[1:]
            return err


class Invalidator(object):
    """Invalidates cache and tests it's invalidation after an action (signal testing)"""
    def __init__(self, case, obj, exist=True):
        self.case = case
        self.obj = obj
        self.key = "key-%d" % id(obj)
        self.exist = exist
        # This assumes LocMem (local memory) cache
        self.cache = TrackCacheMiddleware.cache._cache

    def __enter__(self):
        self.case.assertNotIn(self.key, self.cache)
        self.key = ':1:' + self.key # Add prefix so we can match it later
        TrackCacheMiddleware.cache.set(self.key, "Content", 1000)
        self.case.assertIn(':1:' + self.key, self.cache)
        list(TrackCacheMiddleware.track_cache(self.obj, self.key))

    def __exit__(self, *args):
        if self.exist:
            self.case.assertNotIn(':1:' + self.key, self.cache, "Cache should have been invalidated, but was kept")
        else:
            self.case.assertIn(':1:' + self.key, self.cache, "Cache should have been kept, but was invalidated")


class CacheTests(ExtraTestCase):
    """Test that caches can be invalidated on signals"""
    fixtures = ['cache_objects']

    def setUp(self):
        self.obj = ErrorLog.objects.get(pk=1)
        self.alt = ErrorLog.objects.get(pk=3)
        self.all = ErrorLog.objects.all()
        self.lst = ErrorLog.objects.filter(status=404, count__lt=999)
        self.ast = ErrorLog.objects.filter(status=500, uri='a')
        self.track = lambda o: list(TrackCacheMiddleware.track_cache(o, 'key'))

    def test_tracking_keys(self):
        """Keys returned from tracking objects are as expected"""
        self.assertEqual(self.track(self.obj), ['cache:ErrorLog-1'])
        self.assertEqual(self.track(self.alt), ['cache:ErrorLog-3'])
        self.assertEqual(self.track(ErrorLog), ['cache:ErrorLog'])
        self.assertEqual(self.track(self.all), ['cache:create:ErrorLog'])
        self.assertEqual(self.track(self.lst), ['cache:create:ErrorLog?status=404'])
        self.assertEqual(self.track(self.ast), ['cache:create:ErrorLog?status=500&uri=a'])

    def test_tracking_unique_keys(self):
        """Unique keys for reverse lookups do get cache management"""
        lst = Permission.objects.filter(content_type__id=1)
        self.assertEqual(self.track(lst), ['cache:create:Permission?content_type=1'])

        obj = Group.objects.create(name="Something")

        lst = Permission.objects.filter(group__name="Something")
        self.assertEqual(self.track(lst), ['cache:create:Permission?group=%d' % obj.id])

    def test_tracking_usual_values(self):
        """Lookups with non-unique keys don't get cache management"""
        lst = Permission.objects.filter(group__name="c")
        self.assertEqual(self.track(lst), ['cache:create:Permission'])

        lst = Permission.objects.filter(content_type__app_label="b")
        self.assertEqual(self.track(lst), ['cache:create:Permission'])

        lst = Permission.objects.filter(group__name="Doesn't Exist")
        self.assertEqual(self.track(lst), ['cache:create:Permission'])


    def test_errors_do_not(self):
        """Lookup errors and other items should never die in the cahce middleware"""
        pass # XXX todo

    def test_queryset_wrapper(self):
        """When wrapped, objects accessed add to a list"""
        dest = []
        lst = self.lst._clone(klass=QuerySetWrapper, method=dest.append)
        self.assertEqual(len(dest), 0, "Destination should be empty")
        list(lst)
        self.assertEqual(len(dest), self.lst.count())
        self.assertEqual(type(dest[0]), ErrorLog)
        self.assertEqual(dest[0].pk, 2)
        self.assertEqual(dest[1].pk, 3)

    def assertCacheInvalidate(self, obj):
        """Assert that the cache will be invalidated upon an action:
            
           with self.assertCacheInvalidate(obj):
               pass # perform action here.

        """
        return Invalidator(self, obj, True)

    def assertCacheKept(self, obj):
        """Like assertCacheInvalidate, but tests that the action does not
           invalidate the cache:

           with self.assertCacheKept(obj):
               pass # perform action here.

        """
        return Invalidator(self, obj, False)

    def test_invalidate_edit(self):
        """Test edit invalidates this item's views"""
        with self.assertCacheInvalidate(self.obj):
            self.obj.uri = 'diff'
            self.obj.save()

        with self.assertCacheInvalidate(ErrorLog):
            self.obj.uri = 'again'
            self.obj.save()

    def test_invalidate_delete(self):
        """Test delete invalidates this item's views"""
        with self.assertCacheInvalidate(self.obj):
            self.obj.delete()

        with self.assertCacheInvalidate(ErrorLog):
            self.alt.delete()

    def test_invalidate_create(self):
        """Test create invalidates any simple create: views"""
        with self.assertCacheInvalidate(self.all):
            ErrorLog.objects.create(uri='new', status=1)

        with self.assertCacheInvalidate(ErrorLog):
            ErrorLog.objects.create(uri='new-too', status=2)

    def test_invalidate_one_filter(self):
        """Test create invalidates any queryset's with exact matche filters (one filter)"""
        with self.assertCacheInvalidate(self.lst):
            ErrorLog.objects.create(uri='anything', status=404)

    def test_invalidate_two_filters(self):
        """Test create invalidates any queryset's with exact matche filters (two filters)"""
        with self.assertCacheInvalidate(self.ast):
            ErrorLog.objects.create(uri='a', status=500)

    def test_keep_no_fields(self):
        """Test create does not invalidate other create's (no matching fields)"""
        with self.assertCacheKept(self.lst):
            ErrorLog.objects.create(uri='anything', status=405)

    def test_keep_one_field(self):
        """Test create does not invalidate other create's (one matching field)"""
        with self.assertCacheKept(self.ast):
            ErrorLog.objects.create(uri='a', status=501)



