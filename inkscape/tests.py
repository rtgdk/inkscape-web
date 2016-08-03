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

from django.core.urlresolvers import reverse
from autotest.base import MultipleFailureTestCase

from inkscape.middleware import AutoBreadcrumbMiddleware
from inkscape.url_utils import WebsiteUrls, UrlView

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
            if False and not cache_keys:
                if raw_input("\n\nAre the keys %s correct? [Y/N]: " % ", ".join(keys)) == 'Y':
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

    def test_invalidate_cache(self):
        """Test that caches can be invalidated on signals"""
        # Test edit invalidates this item's views
                              # + this model's generic
        # Test delete invalidates this item's views
                              # + this model's generic
        # Test create invalidates any simple create: views
                              # + this model's generic
        # Test create invalidates any queryset's with exact matche filters (one filter)
        # Test create invalidates any queryset's with exact matche filters (two filters)
        # Test create does not invalidate other create's (no matching fields)
        # Test create does not invalidate other create's (one matching field)
        pass

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
                raise KeyError("Response is not a TemplateResponse (should this be skipped?)")

            if datum.setdefault('breadcrumbs', []) is not None:
                self.assertBreadcrumbResponse(response, **datum)

            print url_str
            if datum.setdefault('cache_keys', []) is not None:
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


