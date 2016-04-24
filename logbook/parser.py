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
Parsing log files for nginx and uwsgi as needed for data processing.
"""

import re
import os
import sys
import urllib

try:
    import user_agents
except ImportError:
    sys.stderr.write("Unable to parse user agents (install module)\n")
    #pylint: disable=invalid-name
    user_agents = None

from collections import Counter, defaultdict
from datetime import datetime, time

from django.contrib.gis.geoip import GeoIP
from django.conf import settings

from logbook.models import LogFile
from logbook.settings import get_setting

def no_bar(*args):
    pass

GEOIP = GeoIP()
def country(value):
    """Returns the country code based on ip address"""
    return str(GEOIP.country_code(value)).lower()

def matches_in(label, filename, rex, progress=no_bar):
    """Finds a match for a regex and yields group dictionaries"""
    size = int(os.stat(filename)[6])
    count = 0
    done = 0
    with open(filename, 'r') as fhl:
        while fhl.tell() < size:
            count += 1
            line = fhl.readline()
            match = rex.match(line.strip())
            if match:
                done += 1
                yield match.groupdict()
            progress(label, fhl.tell() / float(size), count, done)


def parse_logs(location, **kwargs):
    """
    Loop through all defined log types and parse results.
    """
    result = None
    for key in get_setting('LOGS'):
        src = location % {'key': key}
        result = parse_file(key, src, result, **kwargs)
    return result


def parse_file(key, log, result=None, protect=True, **kwargs):
    """
      Parse a log file with the given parser (key) and return a dictionary of
      paths, by a dictionary of dates, with a dictionary of metrics that may
      be a list of all values parsed.
    """
    logs = get_setting('LOGS')
    if key not in logs:
        raise ValueError("Log parser '%s' not found in LOGBOOK_PARSERS" % key)
    logs = logs[key]

    if result is None:
        result = defaultdict(
            lambda: defaultdict(
            lambda: defaultdict(list)))

    if not os.path.isfile(log):
        raise IOError("No %s log to process: %s" % (key, log))

    inode = os.stat(log)[1]
    try:
        LogFile.objects.get(inode=inode)
    except LogFile.DoesNotExist:
        for kwargs in matches_in(key, log, logs['rex'], **kwargs):
            add_result(result, **run(kwargs, *logs.get('ignore', ())))
        if protect:
            LogFile.objects.create(inode=inode)
    else:
        raise IOError("Log file already processed: %s" % log)

    return result


def add_result(result, path, **data):
    """Add a single result to the results matrix"""
    if path is None or not 'date' in data:
        return

    # Index by request path and date
    request = result[path][data.get('date')]
    sitewide = result[None][data.pop('date')]

    ignore = get_setting('IGNORE')
    pathfields = get_setting('PATH_FIELDS')

    # Record all columns regardless
    for key, value in data.items():
        if key in ignore:
            continue
        if key in pathfields:
            request[key].append(value)
        sitewide[key].append(value)


def run(data, *junk):
    """Attempt to format various keys and remove the junk"""
    data['M'] = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].index(data['M'])
    dtm = datetime(*[int(data.pop(k)) for k in ['Y', 'M', 'D', 'h', 'm', 's']])
    data['date'] = dtm.date()
    #data['time'] = time(dtm.time().hour, 0, 0)

    (local, data['lang'], data['path'], _) = url(data['path'])

    for m in get_setting('EXCLUSIONS'):
        if re.match(m, data['path']):
            return {'path': None}

    (local, _, data['refer'], query) = url(data.get('refer', '-'))
    if local:
        data['link'] = data.pop('refer')
    else:
        (data['refer'], data['search']) = get_search(data['refer'] + '?' + query)

    data['count'] = data['path']
    data['country'] = country(data.pop('ip'))
    data.update(dict(get_agent(data.pop('agent', None))))

    if data['status'] != '200':
        junk += ('count', 'country', 'agent')

    for key in junk:
        data.pop(key, None)

    for key, value in data.items():
        if value is None or value == '-':
            data.pop(key)
        # Usually the refer can be long
        if type(value) is str and len(value) > 255:
            data[key] = value[:255]
        if type(value) is tuple:
            if len(value) != 2:
                raise ValueError("Family, name pair error: %s" % str(value))
            data[key] = (value[0][:128], value[1][:255])

    return data


def get_search(url):
    for m in get_setting('SEARCHES'):
        res = re.match(m, url)
        if res:
            return ("search://" + res.groupdict()['site'],
                    res.groupdict().get('q', 'unknown').lower())
    return (url.split('?', 1)[0], None)

# The user agent module is REALLY SLOW so we must
# cache our results here to drasticly improve speed
AGENT_CACHE = {}

def get_agent(agent):
    """Use the user agent string to get browser and os"""
    if agent:
        uid = hash(agent)
        if uid not in AGENT_CACHE:
            if not user_agents:
                sys.stderr.write("Agent not parsed: %d=%s\n" % (uid, agent))
                AGENT_CACHE[uid] = []
            else:
                AGENT_CACHE[uid] = list(agent_filter(parse_agent(agent)))
        return AGENT_CACHE[uid]
    return []


def parse_agent(agent_string):
    """Get the agent string parsed into it's useful parts"""
    agent = user_agents.parse(agent_string)
    # Not sure why user_agents doesn't parse windows
    if agent.os.family.startswith('Windows') and ' ' in agent.os.family:
        yield ('os',) + tuple(agent.os.family.split(' ', 1))
    elif agent.os.family != 'Other':
        yield ('os', agent.os.family, agent.os)

    if agent.browser.family != 'Other':
        yield ('browser', agent.browser.family, agent.browser)

    if agent.device.family != 'Other':
        yield ('device', agent.device.brand, agent.device.family)

def agent_filter(items):
    """Filter user agent items to be more useful"""
    filters = get_setting('FILTERS', {})
    for (kind, family, version) in items:
        version = agent_version(version)
        variable = "%s__%s" % (family, version)
        for (rex, replace) in filters.get(kind, []):
            variable = re.sub(rex, replace, variable, flags=re.IGNORECASE)
            if variable == '':
                break
            elif '__' not in variable:
                raise KeyError("Filter %s not family__version pair." % str(rex))
        if variable != '':
            yield (kind, tuple(variable.split('__', 1)))

def agent_version(agent_item):
    """We want to remove the least significant version information"""
    def lim(val):
        """Limit size of version string"""
        if val >= 1000:
            return str(val)[0] + '0' * (len(str(val)) - 1)
        return str(val)
    if isinstance(agent_item, str):
        return agent_item
    if isinstance(agent_item.version, str):
        return agent_item.version
    return '.'.join([lim(i) for i in agent_item.version[:2]])

def url(path):
    """Seperate out language and standardise url"""
    qs = ''
    local = False
    path = urllib.unquote(path)

    if '?' in path:
        (path, qs) = path.split('?', 1)

    if '://' in path:
        # For refers, we want to shorten them down to local urls.
        server = path.split('://')[-1].split('/')[0]
        if server in settings.ALLOWED_HOSTS:
            path = '/' + path.split('/', 3)[-1]
            local = True

    if path.startswith('/'):
        path = path.lstrip('/')
        if '/' in path:
            (lang, rest) = path.split('/', 1)
            lang = lang.replace('zh-tw', 'zh-hant')
            if lang in get_setting('LANGUAGES'):
                return (True, lang, rest.strip('/'), qs)

    return (local, None, path.strip('/'), qs)

