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
Tests for logbook app.
"""

import sys
import os

from datetime import date

from django.core.urlresolvers import reverse

from logbook.asserting import TestCase, BaseCase, override_settings
from logbook.models import LogName, LogMetric, LogRequest, LogValue, LogPeriod
from logbook.analysis import process_results
from logbook.parser import parse_logs, AGENT_CACHE, user_agents
from logbook.settings import get_setting

WIND = 'download/windows'
LINX = 'download/linux'

if not user_agents:
    # The user_agents module isn't available, so we'll add some cached values
    AGENT_CACHE[-7985492147856592190] = []
    AGENT_CACHE[2307330943812977727] = [('os', ('Windows', '10')), ('browser', ('Chrome', '47'))]
    AGENT_CACHE[8387961549586277991] = [('os', ('Android', '5.1')), ('browser', ('Samsung Internet', '3.4')), ('device', ('Samsung', 'SM-N920C'))]
    AGENT_CACHE[8991742294718112177] = [('os', ('Linux', 'Ubuntu')), ('browser', ('Firefox', '43'))]
    AGENT_CACHE[-3331878396053352693] = [('os', ('Linux', 'Ubuntu')), ('browser', ('Firefox', '42'))]
    AGENT_CACHE[2653303025075231619] = [('browser', ('Bot', 'Baiduspider'))]
    AGENT_CACHE[-126096650150825800] = [('browser', ('Bot', 'bingbot'))]
    AGENT_CACHE[240407478013959810] = [('browser', ('Bot', 'Googlebot'))]
    AGENT_CACHE[-3775843684641215841] = [('os', ('Linux', '3.13')), ('browser', ('Bot', 'Python Requests'))]
    AGENT_CACHE[-3023881853768432087] = [('browser', ('Bot', 'Apache-HttpClient'))]
    AGENT_CACHE[-2671430300838129903] = [('browser', ('Bot', 'ZEEFscraper'))]
    AGENT_CACHE[-5685902084964927210] = [('browser', ('Bot', 'Sogou web spider'))]
    AGENT_CACHE[-421933450344972659] = [('browser', ('Bot', 'Googlebot-Image'))]
    AGENT_CACHE[3948824748557086037] = [] #('browser', ('Bot', 'Feedbin'))]


@override_settings(LOGBOOK_TEST="Foo")
class SettingsTest(TestCase):
    def test_default_setting(self):
        self.assertIn('size', get_setting('UNITS'))

    def test_error_setting(self):
        self.assertRaises(KeyError, get_setting, 'NOTHING')
        self.assertRaises(IOError, get_setting, 'TEST_ERROR')

    def test_regex(self):
        self.assertIn('rex', get_setting('LOGS')['nginx'])

    def test_override(self):
        self.assertEqual(get_setting('TEST'), 'Foo')


class OtherTests(BaseCase):
    """Other indervidual tests"""
    def test_file_protection(self):
        """We refuse to process the same file"""
        parse_logs(self.get_log('basic'))
        self.assertRaises(IOError, parse_logs, self.get_log('basic'))

    def test_addition(self):
        """Dates shouldn't clobber previous data"""
        for x in range(1, 4):
            process_results({None: {date(2001, 1, 1): {
                'browser': [('Firefox', '44'), ('Firefox', '44')],
                'delay': [100 * x, 20 * x],
                }}})
            self.assertObjects(
                LogValue.objects.filter(metric__name__in=['browser', 'delay']),
                ['count', 'avg', 'low', 'high'],
                (x * 2, None, None, None),
                (x * 2, [0, 60, 90, 120][x], 20, 100 * x)
            )


class BasicAnalysisTests(BaseCase):
    """Test a single request to the database"""
    def setUp(self):
        """Parse a log file in fixtures, analyse and compare to result"""
        process_results(parse_logs(self.get_log('basic')))

    def test_metric_creations(self):
        """We expect delay to not be here this time."""
        self.assertObjectCols(LogMetric, ['name', 'unit'],
            ('status', 'size', 'delay', 'link', 'lang', 'country',
             'count', 'os', 'browser'),
            ('bytes', 'ms') + (None,) * 7,
        )

    def test_name_creations(self):
        """We expect only named items and families to be dynamic"""
        self.assertObjectCols(LogName, ['name', 'family'],
            ('10', 'en', WIND, '200', 'jp', '47'),
            ('Windows', 'Chrome', None, None, None, None),
        )

    def test_period_creations(self):
        """There should only be two periods"""
        self.assertObjects(LogPeriod,
            ['period', 'date', 'request__path'],
            (0, '2016-01-05', None),
            (0, '2016-01-05', WIND),
        )

    def test_values(self):
        """The values should be correct for a single line"""
        self.assertObjects(LogValue,
            ['metric__name', 'period__date', 'period__request__path',
             'name__name', 'count', 'avg'],
            # METRIC,   PERIOD,    REQUEST, NAME, COUNT, AVG
            ('browser', '2016-01-05', None, '47', 1, None),
              ('count', '2016-01-05', None, WIND, 1, None),
            ('country', '2016-01-05', None, 'jp', 1, None),
              ('delay', '2016-01-05', None, None, 1, 239),
              ('delay', '2016-01-05', WIND, None, 1, 239),
               ('lang', '2016-01-05', None, 'en', 1, None),
               ('link', '2016-01-05', None, WIND, 1, None),
               ('link', '2016-01-05', WIND, WIND, 1, None),
                 ('os', '2016-01-05', None, '10', 1, None),
               ('size', '2016-01-05', None, None, 1, 3391),
               ('size', '2016-01-05', WIND, None, 1, 3391),
             ('status', '2016-01-05', None, '200', 1, None),
             ('status', '2016-01-05', WIND, '200', 1, None),
        )


class MultiAnalysisTests(BaseCase):
    """Test a many requests to the database"""
    def setUp(self):
        """Parse a log file in fixtures, analyse and compare to result"""
        process_results(parse_logs(self.get_log('multi')))

    def test_metric_creations(self):
        """We expect metric names to be dynamic."""
        self.assertObjectCols(LogMetric, ['name', 'unit'],
            ('status', 'size', 'refer', 'lang', 'link',
             'search', 'country', 'count', 'os', 'browser'),
            ('bytes',) + (None,) * 9,
        )

    def test_period_creations(self):
        """There should only be two periods"""
        self.assertObjects(LogPeriod,
            ['period', 'date', 'request__path'],
            (0, '2016-01-05', None),
            (0, '2016-01-05', ''),
            (0, '2016-01-05', LINX),
            (0, '2016-01-05', WIND),
            (0, '2016-01-06', None),
            (0, '2016-01-06', WIND),
            (0, '2016-01-07', None),
            (0, '2016-01-07', WIND),
            (2, '2016-01-03', None),
            (2, '2016-01-03', WIND),
            (3, '2016-01-01', None),
            (3, '2016-01-01', WIND),
            (4, '2016-01-01', None),
            (4, '2016-01-01', WIND),
        )

    def test_request_periods(self):
        """Requests can lead to periods"""
        request = LogRequest.objects.get(path=None)
        today = date(2016, 01, 10)
        data = request.days(today=today)
        self.assertTrue(data)
        self.assertEqual(data[0][0].name, 'browser')
        self.assertTrue(list(data[0][1]))

        self.assertTrue(request.week_days(today=today))
        self.assertTrue(request.weeks(today=today))
        self.assertTrue(request.months(today=today))
        self.assertTrue(request.years(today=today))

    def test_count_value(self):
        """The browser counts should be correct for many lines"""
        self.assertObjects(LogValue.objects.filter(metric__name='browser'),
            ['metric__name', 'period__date', 'name__family',
             'name__name', 'count', 'avg'],
            # METRIC,   PERIOD,       FAMILY,   NAME, COUNT, AVG
            ('browser', '2016-01-05', 'Firefox', '43', 4, None),
            ('browser', '2016-01-05', 'Chrome', '47', 6, None),
            ('browser', '2016-01-06', 'Chrome', '47', 1, None),
            ('browser', '2016-01-07', 'Chrome', '47', 1, None),
            ('browser', '2016-01-03', 'Chrome', '47', 8, 2),
            ('browser', '2016-01-01', 'Chrome', '47', 8, 2),
            ('browser', '2016-01-01', 'Chrome', '47', 8, 2),
        )

    def test_avg_value(self):
        """The size calculations should be averages"""
        self.assertObjects(LogValue.objects.filter(metric__name='size'),
            ['metric__name', 'period__date', 'period__request__path',
                'period__period', 'count', 'low', 'high', 'avg'],
            ('size', '2016-01-05', None, 0, 12, 1102, 8932, 3329),
            ('size', '2016-01-05', '', 0, 2, 1391, 1391, 1391),
            ('size', '2016-01-05', LINX, 0, 4, 1391, 8901, 4235),
            ('size', '2016-01-05', WIND, 0, 6, 1102, 8932, 3370),
            ('size', '2016-01-06', None, 0, 1, 1103, 1103, 1103),
            ('size', '2016-01-06', WIND, 0, 1, 1103, 1103, 1103),
            ('size', '2016-01-07', None, 0, 1, 1104, 1104, 1104),
            ('size', '2016-01-07', WIND, 0, 1, 1104, 1104, 1104),
            ('size', '2016-01-03', None, 2, 14, 1102, 8932, 395),
            ('size', '2016-01-03', WIND, 2, 8, 1102, 8932, 697),
            ('size', '2016-01-01', None, 3, 14, 1102, 8932, 395),
            ('size', '2016-01-01', WIND, 3, 8, 1102, 8932, 697),
            ('size', '2016-01-01', None, 4, 14, 1102, 8932, 395),
            ('size', '2016-01-01', WIND, 4, 8, 1102, 8932, 697),
        )

class ParsingTests(BaseCase):
    def test_search_log(self):
        """Search logs are parsed for any data"""
        res = parse_logs(self.get_log('search'))[None][date(2016, 1, 5)]
        self.assertEqual(res['refer'], [
            'search://yahoo',
            'search://thesmartsearch',
            'search://google',
            'search://duckduckgo',
            'search://yandex',
            'search://ecosia',
            'search://qwant',
        ])
        self.assertEqual(res['search'], [
            'inkscape+\xe7\x84\xa1\xe6\x96\x99\xe3\x80\x80\xe3\x83\x80\xe3\x82\xa6\xe3\x83\xb3\xe3\x83\xad\xe3\x83\xbc\xe3\x83\x89',
            'inkscape',
            'inkscape+manual',
            'inkscape filter texture copyright',
            'unknown',
            'inkscape',
            'inkscape'
        ])

    def test_basic_log(self):
        """Single request gives a single response"""
        self.assertParseLog('basic', {
          None: {date(2016, 1, 5): {
            'browser': [('Chrome', '47')],
            'count': ['download/windows'],
            'country': ['jp'],
            'lang': ['en'],
            'os': [('Windows', '10')],
            'link': ['download/windows'],
            'size': ['3391'],
            'status': ['200'],
            'delay': ['239'],
            }},\
          'download/windows': {date(2016, 1, 5): {
            'link': ['download/windows'],
            'size': ['3391'],
            'status': ['200'],
            'delay': ['239'],
          }},
        })

    def test_agent_filters(self):
        """The user agents should be filtered"""
        process_results(parse_logs(self.get_log('agents')))
        self.assertObjects(LogValue.objects.filter(metric__name='os'),
            ['name__family', 'name__name'],
            ('Linux', '3.13'),
            ('Android', '5.1'),
        )
        self.assertObjects(LogValue.objects.filter(metric__name='device'),
            ['name__family', 'name__name'],
            ('Samsung', 'SM-N920C'),
        )
        self.assertObjects(LogValue.objects.filter(metric__name='browser'),
            ['name__family', 'name__name'],
            ('Samsung Internet', u'3.4'),
            ('Bot', 'Apache-HttpClient'),
            ('Bot', 'Baiduspider'),
            ('Bot', 'bingbot'),
            ('Bot', 'Googlebot'),
            ('Bot', 'Googlebot-Image'),
            ('Bot', 'Python Requests'),
            ('Bot', 'Sogou web spider'),
            ('Bot', 'ZEEFscraper'),
        )

    def test_long_log(self):
        """A log line with long names"""
        AGENT_CACHE[hash('LENTEST')] = [
            ('os', ("FAM" * 300, "VER" * 300)),
            ('device', ("FAM" * 300, "BRAND" * 100)),
            ('browser', ("FAM" * 300, "VER" * 300)),
        ]
        ret = parse_logs(self.get_log('long'))[None].values()[0]
        self.assertEqual(ret['count'][0][:10], 'folderuri/')
        self.assertEqual(len(ret['count'][0]), 255)
        self.assertEqual(ret['link'][0][:10], 'refer_uri/')
        self.assertEqual(len(ret['link'][0]), 255)

        self.assertEqual(ret['browser'][0][1][:3], 'VER')
        self.assertEqual(len(ret['browser'][0][1]), 255)
        self.assertEqual(ret['browser'][0][0][:3], 'FAM')
        self.assertEqual(len(ret['browser'][0][0]), 128)

        self.assertEqual(ret['device'][0][1][:3], 'BRA')
        self.assertEqual(len(ret['device'][0][1]), 255)
        self.assertEqual(ret['device'][0][0][:3], 'FAM')
        self.assertEqual(len(ret['device'][0][0]), 128)

    def test_multi_log(self):
        """Ten requests gives interesting results"""
        self.assertParseLog('multi', {
          None: {date(2016, 1, 5): {
            'browser': [('Chrome', '47')] * 6 + [('Firefox', '43')] * 4,
            'count': ['download/windows'] * 6 + ['download/linux', ''] * 2,
            'country': ['br'] * 7 + ['jp'] * 3,
            'lang': ['en', 'fr'] * 5 + ['fr', 'zh-hant'],
            'os': [('Linux', 'Ubuntu')] * 4 + [('Windows', '10')] * 6,
            'link': ['download/windows'] * 6 + ['download'] * 3 + [''] * 2,
            'refer': ['search://google'],
            'size': ['1102', '1191', '1205', '1391', '1391', '1391', '3291',
                     '3300', '3351', '4504', '8901', '8932'],
            'search': ['inkscape'],
            'status': ['200'] * 10 + ['404'] * 2,
          }, date(2016, 1, 6): {
            'browser': [('Chrome', '47')],
            'count': ['download/windows'],
            'country': ['jp'],
            'lang': ['en'],
            'os': [('Windows', '10')],
            'link': ['download/windows'],
            'size': ['1103'],
            'status': ['200'],
          }, date(2016, 1, 7): {
            'browser': [('Chrome', '47')],
            'count': ['download/windows'],
            'country': ['jp'],
            'lang': ['en'],
            'os': [('Windows', '10')],
            'link': ['download/windows'],
            'size': ['1104'],
            'status': ['200'],
          }},
          'download/linux': {date(2016, 1, 5): {
            'link': ['download'] + ['download/windows'] * 3,
            'size': ['1391', '3300', '3351', '8901'],
            'status': ['200', '200', '404', '404'],
          }},
          '': {date(2016, 1, 5): {
            'link': [''] * 2,
            'size': ['1391', '1391'],
            'status': ['200', '200'],
          }},
          'download/windows': {date(2016, 1, 5): {
            'link': ['download/windows'] * 3 + ['download'] * 2,
            'refer': ['search://google'],
            'size': ['1102', '1191', '1205', '3291', '4504', '8932'],
            'status': ['200', '200', '200', '200', '200', '200'],
            'search': ['inkscape'],
          }, date(2016, 1, 6): {
            'link': ['download/windows'],
            'size': ['1103'],
            'status': ['200'],
          }, date(2016, 1, 7): {
            'link': ['download/windows'],
            'size': ['1104'],
            'status': ['200'],
          }},
        })


class DataReportTests(BaseCase):
    def setUp(self):
        process_results(parse_logs(self.get_log('reportable')))
        self.metric = LogMetric.objects.get(name='browser')

    def assertJsonRequest(self, name, get=None, kwargs=None, **equals):
        if name[0] == '/':
            url = name
        else:
            url = reverse(name, kwargs=kwargs)
        response = self.client.get(url, get)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content), equals)
        return response.content


    def test_00_raw_data(self):
        (family, names) = zip(*self.metric.families())
        (names, counts) = zip(*[name[0] for name in names])
        self.assertEqual(family, ('Chrome', 'Firefox'))
        self.assertEqual(names, ('47', '43'))
        self.assertEqual(counts, (208, 65))

    def test_01_data_table(self):
        self.assertJsonRequest('logbook:metric.json', )

    def test_02_pie_data(self):
        pass

    def test_03_line_data(self):
        pass





