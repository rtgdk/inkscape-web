#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
Base testing functions
"""

# FLAG: do not report failures from here in tracebacks
#__unittest = True


import sys
import os

from unittest.case import SkipTest

from django.db import connection
from django.db.models import Model
from django.test import TestCase, override_settings

from logbook.orderedset import OrderedSet
from logbook.parser import parse_logs

ROOT_DIR = os.path.dirname(__file__)

@override_settings(
    ALLOWED_HOSTS=['inkscape.org'],
    LOGBOOK_ROOT=os.path.join(ROOT_DIR, 'fixtures', 'logs')
  )
class BaseCase(TestCase):
    dirname = os.path.join(os.path.dirname(__file__), 'fixtures', 'logs')
    fixtures = []

    def setUp(self):
        """Skip tests if we aren't using postgresql"""
        super(BaseCase, self).setUp()
        if 'sqlite' in connection.vendor:
            raise SkipTest("Sqlite orders None values differently")

    def get_log(self, src):
        """Returns a log file at a known location"""
        return os.path.join(self.dirname, src + '-%(key)s.log')

    def assertValuesList(self, expected, got, msg=None, sort=False):
        """Prepare a list of db values for comparison"""
        def prepare(lst):
            """Filter out db values that don't compare"""
            lst = list(lst)
            for index, val in enumerate(lst):
                if isinstance(val, (str, unicode, int, float, long)):
                    continue
                else:
                    lst[index] = str(val)
            if sort:
                lst.sort()
            return lst
        self.assertEqual(prepare(expected), prepare(got), msg)

    def assertValuesLists(self, expected, got, msg=None, sort=False):
        """Two values lists of lists are equal"""
        def item(lst):
            """Unpack list items for debug"""
            if not sort:
                return ["'%s'" % str(i) for i in lst]
            return ["'%s'=%d" % (str(i), lst.count(i)) for i in set(lst)]

        def dbg(a, b):
            """Debug string for value size different"""
            if len(a) < len(b):
                (a, b) = (b, a)
            elif len(a) == len(b):
                return []
            msg = ''
            for diff in OrderedSet(a) ^ OrderedSet(b):
                msg += " %s %s\n" % ('+-'[diff in a], str(diff))
            return msg

        self.assertEqual(len(expected), len(got),
                "Expected %d rows, got %d rows:\n%s" % (
            len(expected), len(got), dbg(expected, got)))

        for index, item in enumerate(expected):
            self.assertValuesList(item, got[index], msg, sort)

    def assertIsFile(self, filename):
        """Asserts that a file exists"""
        self.assertTrue(os.path.isfile(filename),
            "File not found: %s" % filename)

    def assertSubEqual(self, key, a, b):
        """Are two sub lists in a dictonary the same?"""
        self.assertIn(key, a)
        if isinstance(a[key], (list, tuple, dict)):
            self.assertEqual(sorted(a[key]), sorted(b[key]))
        else:
            self.assertEqual(a[key], b[key])

    def assertStructure(self, parsed, result):
        """Is the parsed structure what we expect to find?"""
        self.assertEqual(list(parsed), list(result))
        (path, t_date, field) = ('', '', '')
        try:
            for path in parsed:
                self.assertSubEqual(path, parsed, result)
                for t_date in parsed[path]:
                    self.assertSubEqual(t_date, parsed[path], result[path])
                    for field in parsed[path][t_date]:
                        self.assertSubEqual(field,
                            parsed[path][t_date], result[path][t_date])
        except AssertionError:
            sys.stderr.write("Info: %s / %s / %s" % (path, str(t_date), field))
            raise

    def assertParseLog(self, src, result):
        """Parse a log file in fixtures and compare to result"""
        return self.assertStructure(parse_logs(self.get_log(src)), result)

    def assertObjectCols(self, cls, fields, *exp, **kwargs):
        """Assert columns by rotating object data"""
        qs = cls.objects if hasattr(cls, 'objects') else cls
        self.assertValuesLists(exp, zip(*qs.values_list(*fields)), sort=True)

    def assertObjects(self, cls, fields, *exp, **kwargs):
        """Assert columns from model in database"""
        qs = cls.objects if hasattr(cls, 'objects') else cls
        self.assertValuesLists(exp, qs.values_list(*fields), sort=False)

    def assertJsonRequest(self, name, *args, **equals):
        if name[0] == '/':
            url = name
        else:
            url = reverse(name, kwargs=kwargs)
        response = self.client.get(url, get)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content), equals)
        return response.content

