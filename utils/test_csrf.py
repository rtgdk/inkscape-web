#!/bin/bash

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

# This script is attempting to test the cookie setting properties of the website.

import time
import sys
import os

url = 'http://localhost:8000/en/'
url = 'https://inkscape.org/en/'
url = 'http://staging.inkscape.org/en/'
cookie = '/tmp/cookie'
line = 'wget --save-cookies %s %s -O /tmp/out -o /tmp/prog' % (cookie, url)

def request():
    os.system(line)
    with open(cookie, 'r') as fhl:
        ret = fhl.read()
        if 'csrftoken' not in ret:
            return 1
    return 0

print "Testing %s" % url

x = 0
for i in range(1, 100):
    x += request()
    if i % 10 == 0:
        print "Made %d requests of which %d were broken (%d%%)" % (i, x, (float(x)/i)*100)

