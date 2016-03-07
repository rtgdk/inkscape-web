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
LogBook app settings
"""

from django.conf import settings

ROOT = IOError("Please define a LOGBOOK_ROOT where your logs can be found.")

LANGUAGES = zip(*settings.LANGUAGES)[0]

UNITS = {
  'size': 'bytes',
  'delay': 'ms',
}

EXCLUSIONS = [
    r'^favicon.ico$',
    r'^static/',
    r'^media/',
    r'^admin/',
    r'^moderation/',
    r'^user/activate',
    r'^user/pwd',
]

SEARCHES = [
    r'https?://(www\.|search\.)?(?P<site>[^\.]+).*[\?&]q=(?P<q>[^&]+).*',
    r'https?://(www\.|search\.)?(?P<site>[^\.]+).*\/search\?(.*)p=(?P<q>[^&]+).*',
    r'https?://(www\.|search\.)?(?P<site>(google|yahoo|bing|yandex|qwant|duckduckgo))',
]

IGNORE = ['rest', 'method']

PATH_FIELDS = ['size', 'delay', 'refer', 'link', 'status', 'search']

LOGS = {
    # Nginx tells us the os and browser, language and most info.
    'nginx': {
      'pattern':
        r'^(?P<ip>\d+\.\d+\.\d+\.\d+)'
        r' - - '
        r'\[(?P<D>\d+)\/(?P<M>[a-zA-Z]+)\/(?P<Y>\d+):'
        r'(?P<h>\d+):(?P<m>\d+):(?P<s>\d+) (?P<tz>[+\-]\d+)\] '
        r'\"(?P<method>[A-Z]+) '
        r'(?P<path>\/[^\s]*) '
        r'HTTP\/1.1\" '
        r'(?P<status>\d+) '
        r'(?P<size>\d+) '
        r'\"(?P<refer>[^\"]+)\" '
        r'\"(?P<agent>[^\"]+)\"'
        r'(?P<rest>.*)$',
      'ignore': ('rest', 'other', 'tz'),
    },
    # Wsgi tells us how long requests took, we could take other information
    'wsgi': {
      'pattern':
        r'^\[pid\: (?P<pid>\d+)'
        r'\|app\: (?P<app>\d+)'
        r'\|req\: \d+\/\d+\] '
        r'(?P<ip>[\d\.]+) \(\) '
        r'\{\d+ vars in \d+ bytes\} '
        r'\[\w\w\w (?P<M>\w\w\w) (?P<D>\d+) '
        r'(?P<h>\d+):(?P<m>\d+):(?P<s>\d+) '
        r'(?P<Y>\d+)\] '
        r'(?P<method>\w+) '
        r'(?P<path>[^\s]+) => '
        r'generated (?P<size>\d+) bytes '
        r'in (?P<delay>\d+) msecs '
        r'\(HTTP\/1.[10] (?P<status>\w+)\) '
        r'\d+ headers in \d+ bytes '
        r'\(\d+ switches on core \d+\)'
        r'(?P<rest>.*)$',
      'ignore': ('app', 'pid', 'country', 'size', 'method', 'status', 'count')
    },
}

FILTERS = {
  'browser': [
    (r'(.*)__(\d+)\.0+$', r'\1__\2'),
    (r'(.*(bot|spider|scraper|crawler|python|archiv|scrapy|sleuth|phantomjs|simplepie|bing|winhttp|apache|robots).*)__(.*)', r'Bot__\1'),
    (r'(.*(ning|facebook|pinterest|wordpress|twitter).*)__(.*)', r'Social Feed__\1'),
    (r'(.*(mail|outlook|thunderbird).*)__(.*)', r'Mail__\1'),
    (r'(.*)(mobile|mini|tablet)(.*)__(.*)', r'\1\3__\4M'),
    (r'(.*)(nightly|alpha|beta|frame)(.*)__(.*)', r'Development__\1\3'),
    (r'(.*)(ios|iphone)(.*)__(.*)', r'\1\3__\4'),
  ],
  'os': [
    (r'(.*)__$', r'\1__Unknown'),
    (r'(ios)__(\d).+', r'\1__\2'),
    (r'(chrome os)__(\d)\d\d\d\.\d+', r'\1__\2k'),
    (r'(.*)(symbian)(.*)__(.*)', r'\2__\3'),
    (r'(.*)(openbsd|freebsd)(.*)__(.*)', r'BSD__\2'),
    (r'(.*(ubuntu|fedora|suse|debian).*)__(.*)', r'Linux__\1'),
    (r'linux__linux', r'linux__unknown'),
  ],
  'device': [
    (r'^.*spider.*$', r''),
    (r'^.*unversioned.*$', r''),
    (r'^(.*)__\1 \1 (.*)', r'\1__\2'),
    (r'^(.*)__\1 (.*)', r'\1__\2'),
    (r'(.*)__(nexus .*)', r'Asus__\2'),
    (r'(sonyericsson)__(.*)', r'Sony__SonyEricsson \2'),
    (r'generic_android__.*tablet.*', r'Generic__Tablet'),
    (r'generic_android__(.*)', r'Generic__Android'),
  ],
}

# Used to test settings (do not override)
TEST_ERROR = IOError("Caused an error")

def get_setting(key, value=KeyError, prefix='LOGBOOK'):
    """
      Attempt to get site settings, fall back to app setting,
      raise an exception if the value is requird.

      The default prefix is 'LOGBOOK'
    """
    value = getattr(settings, prefix + '_' + key,
               globals().get(key, value))
    if isinstance(value, Exception):
        raise value
    elif value is KeyError:
        raise value("Setting not found: %s" % key)
    compiler = 'compile_' + key.lower()
    if compiler in globals():
        return globals()[compiler](value)
    return value

def compile_logs(logs):
    """Compile the regular expression for each log parser"""
    import re
    for item in logs.values():
        item['rex'] = re.compile(item['pattern'])
    return logs

