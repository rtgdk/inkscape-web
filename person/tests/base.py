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
Test user and team functions
"""

# FLAG: do not report failures from here in tracebacks
__unittest = True

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from user_sessions.utils.tests import Client

class BaseUserCase(TestCase):
    fixtures = ['test-auth']

    def setUp(self):
        super(BaseUserCase, self).setUp()
        self.client = Client()
        self.user = authenticate(username='tester', password='123456')
        self.client.login(username='tester', password='123456')

    def assertGet(self, url_name, *arg, **kw):
        "Make a generic GET request with the best options"
        status = kw.pop('status', 200)
        data = kw.pop('data', {}) 
        method = kw.pop('method', self.client.get)
        follow = kw.pop('follow', True)
        get_param = kw.pop('get_param', None)
        if url_name[0] == '/':
            url = url_name
        else:
            url = reverse(url_name, kwargs=kw, args=arg)
        if get_param:
            url += '?' + get_param 
        response = method(url, data, follow=follow)
        self.assertEqual(response.status_code, status)
        return response
    
    def assertPost(self, *arg, **kw):
        "Make a generic POST request with the best options"
        kw['method'] = self.client.post
        return self.assertGet(*arg, **kw)


