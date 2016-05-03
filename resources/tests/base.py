#
# Copyright 2015, Maren Hachmann <marenhachmann@yahoo.com>
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
Base TestCase for Resource and Gallery Tests.
"""

# FLAG: do not report failures from here in tracebacks
# pylint: disable=invalid-name
__unittest = True

import os
import types
import shutil
import haystack

from os.path import dirname, join, abspath
from datetime import date

from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth import authenticate
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.core.files.base import File

from user_sessions.backends.db import SessionStore
from user_sessions.utils.tests import Client

from django.http import HttpRequest
from django.conf import settings

from resources.models import ResourceFile
from inkscape.middleware import AutoBreadcrumbMiddleware

TEST_INDEX = {
  'default': {
    'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
    'STORAGE': 'ram',
  },
}

DIR = dirname(__file__)
MEDIA = settings.MEDIA_ROOT.rstrip('/') + '_test'
SOURCE = os.path.join(DIR, '..', 'fixtures', 'media', 'test')

@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX, MEDIA_ROOT=MEDIA)
class BaseCase(TestCase):
    fixtures = ['test-auth', 'licenses', 'categories', 'quota', 'resource-tests'
               ]

    def open(self, filename, *args, **kw):
        "Opens a file relative to this test script"
        if not '/' in filename:
            filename = join(SOURCE, filename)
        return File(open(join(DIR, filename), *args), **kw)

    def getObj(self, qs, **kw):
        """
        Get an object from django, assert it exists, return it.

        qs      - a QuerySet or Model class
        count   - number of objects to get (default: 1)
        exclude - exclude filter to run (default: None)
        **kw    - include filter to run (default: None)
        """
        count = kw.pop('count', 1)

        # Is the queryset a class? It's probably a model class
        if isinstance(qs, (types.TypeType, types.ClassType)):
            qs = qs.objects.all()

        if 'exclude' in kw:
            qs = qs.exclude(**kw.pop('exclude'))
        if kw:
            qs = qs.filter(**kw)

        # Assert we have enough objects to return
        self.assertGreater(qs.count(), count - 1)

        # Return either one object or a list of objects limited to count
        return qs[0] if count == 1 else qs[:count]

    def assertGet(self, url_name, *arg, **kw):
        "Make a generic GET request with the best options"
        data = kw.pop('data', {})
        method = kw.pop('method', self.client.get)
        follow = kw.pop('follow', True)
        status = kw.pop('status', None)
        get_param = kw.pop('get_param', None)

        if url_name[0] == '/':
            url = url_name
        else:
            url = reverse(url_name, kwargs=kw, args=arg)
        if get_param:
            url += '?' + get_param

        response = method(url, data, follow=follow)
        if status:
            self.assertEqual(response.status_code, status)
        return response

    def assertPost(self, *arg, **kw):
        "Make a generic POST request with the best options"
        errs = kw.pop('form_errors', None)
        kw['method'] = self.client.post
        response = self.assertGet(*arg, **kw)

        if errs:
            for (field, msg) in errs.items():
                self.assertFormError(response, 'form', field, msg)
        elif response.context and 'form' in response.context:
            form = response.context['form']
            if 'status' in kw and kw['status'] == 200 and form:
                msg = ''
                for field in form.errors:
                    msg += "%s: %s\n" % (field, ','.join(form.errors[field]))
                self.assertFalse(bool(form.errors), msg)
        return response

    def set_session_cookies(self):
        """Set session data regardless of being authenticated"""

        # Save new session in database and add cookie referencing it
        request = HttpRequest()
        request.session = SessionStore('Python/2.7', '127.0.0.1')

        # Save the session values.
        request.session.save()

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.client.cookies[session_cookie] = request.session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }
        self.client.cookies[session_cookie].update(cookie_data)

    def setUp(self):
        "Creates a dictionary containing a default post request for resources"
        super(TestCase, self).setUp()
        self.client = Client()

        media = os.path.join(MEDIA, 'test')
        if not os.path.isdir(media):
            os.makedirs(media)
        for fname in os.listdir(SOURCE):
            target = os.path.join(media, fname)
            if not os.path.isfile(target):
                shutil.copy(os.path.join(SOURCE, fname), target)

        haystack.connections.reload('default')
        call_command('rebuild_index', interactive=False, verbosity=0)

        self.download = self.open('file5.svg')
        self.thumbnail = self.open('preview5.png')
        self.data = {
          'download': self.download,
          'thumbnail': self.thumbnail,
          'name': 'Test Resource Title',
          'link': 'http://www.inkscape.org',
          'desc': 'My nice picture',
          'category': 2,
          'license': 4,
          'owner': 'True',
          'published': 'on',
        }

    def tearDown(self):
        call_command('clear_index', interactive=False, verbosity=0)
        super(TestCase, self).tearDown()
        self.download.close()
        self.thumbnail.close()

class BaseUserCase(BaseCase):
    def setUp(self):
        super(BaseUserCase, self).setUp()
        self.user = authenticate(username='tester', password='123456')
        self.client.login(username='tester', password='123456')

class BaseAnonCase(BaseCase):
    def setUp(self):
        super(BaseAnonCase, self).setUp()
        self.set_session_cookies()

    def assertEndorsement(self, endorse=ResourceFile.ENDORSE_NONE, **kw):
        rec = ResourceFile.objects.filter(**kw)
        self.assertGreater(rec.count(), 0, "No resources with: %s" % str(kw))

        for resource in rec:
            self.assertEqual(resource.endorsement(), endorse,
                "Endorsement doesn't match for file: %s and sig %s" %
                (resource.download, resource.signature))


class BaseBreadcrumbCase(BaseAnonCase):
    def assertBreadcrumbRequest(self, url, *terms, **kwargs):
        cont = self.assertGet(url, **kwargs).content
        crumbs = cont.split('breadcrumbs">', 1)[-1].split('</div>')[0]
        try:
            for x, term in enumerate(terms):
                if len(term) == 1:
                    self.assertIn('<em class="crumb">%s<' % term, crumbs)
                elif x == len(terms) - 1 and len(terms) != 1:
                    self.assertIn('<em class="crumb">%s<' % term[1], crumbs)
                else:
                    self.assertIn('href="%s" class="crumb">%s<' % term, crumbs)
        except AssertionError:
            raise AssertionError("Breadcrumb %s missing from %s" % (
                str(term), crumbs))

    def assertBreadcrumbs(self, obj, *terms, **kwargs):
        """Test breadcrumbs in both generation and template request"""
        crumbs = list(AutoBreadcrumbMiddleware()._crumbs(object=obj, **kwargs))
        (links1, names1) = zip(*crumbs)
        (links2, names2) = zip(*terms)
        # The i18n gets in the way of testing the names
        #self.assertTupleEqual(names1, names2)
        self.assertTupleEqual(links1, links2)
        if hasattr(obj, 'get_absolute_url'):
            self.assertBreadcrumbRequest(obj.get_absolute_url(), *terms)

