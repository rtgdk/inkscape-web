#!/bin/bash
#
# This script is attempting to test the cookie setting properties of the website.
#

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

