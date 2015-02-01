#!/usr/bin/python
#
# 2015 - This is a very rough script for grabbing uptime data from nginx logs.
#

import sys
import os
import re

from datetime import datetime, date, time
from collections import defaultdict

class Entry(object):
    def __init__(self):
        self.count = 0
        self.size = 0
        self.large = 0
        #self.scales = defaultdict(int)

    def __add__(self, size):
        self.count += 1
        self.size += size
        #if len(str(size)) > 5:
        #    self.scales[ len(str(size)) - 5 ] += 1
        if self.large < size:
            self.large = size
        return self

    @property
    def _large(self):
        ret = ','.join([ str(self.scales.pop(s+1, 0)) for s in range(4) ])
        if self.scales:
            raise ValueError("Still have %d left\n" % str(self.scales))
        return ret


LINE_RE = r'^(?P<ipaddress>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<dateandtime>\d{2}\/[a-zA-Z]{3}\/\d{4}:\d{2}:\d{2}:\d{2}) (\+|\-)(\d{4})\] \"(\w+) ?(?P<url>.+)(HTTP\/\d\.\d)\" (?P<statuscode>\d{3}) (?P<bytessent>\d+) ["](?P<refferer>\-|.+)["] ["](?P<useragent>.+)["]'

MONTHS = ['', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

TIMES = defaultdict(Entry)
MINS = 1

for line in sys.stdin.readlines():
    datum = re.findall(LINE_RE, line)
    if datum:
        (ip, dt, _m, _tz, method, uri, _http, status, size, refferer, agent) = datum[0]
        if status != '200' or method not in ['POST', 'GET']:
            continue
        (hour, minute, second) = dt.split(':')[1:]
        t = time( int(hour), int(minute)/MINS*MINS, 0 )
        (day, month, year) = dt.split(':')[0].split('/')
        d = date(*[int(year), MONTHS.index(month.lower()), int(day)])
        key = "%s %s" % (str(d), str(t))
        TIMES[key] += int(size)

for t in sorted(TIMES.keys()):
    if t > "2015-01-29 20:00:00" and t < "2015-01-29 23:00:00":
        print ",".join([str(t), str(TIMES[t].count), str(TIMES[t].size), str(TIMES[t].large)])


