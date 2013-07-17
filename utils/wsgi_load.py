#!/usr/bin/python2.7

import os
import sys

_VER = "python2.7" #"python%d.%d" % (sys.version_info[0], sys.version_info[1])

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
if 'utils' in PROJECT_PATH:
    PROJECT_PATH = os.path.dirname(PROJECT_PATH)
ACTIVATE = os.path.join(PROJECT_PATH, 'pythonenv/bin/activate_this.py')
PYTHONS = os.path.join(PROJECT_PATH, 'pythonenv', 'lib', _VER, 'site-packages')

sys.path.insert(0, PROJECT_PATH)
sys.path.insert(0, PYTHONS)

execfile( ACTIVATE, dict(__file__=ACTIVATE) )

os.environ['DJANGO_SETTINGS_MODULE'] = 'inkscape.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

