#!/usr/bin/python

import os
import sys

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
if 'utils' in PROJECT_PATH:
    PROJECT_PATH = os.path.dirname(PROJECT_PATH)
ACTIVATE = os.path.join(PROJECT_PATH, 'pythonenv/bin/activate_this.py')

sys.path.insert(0, PROJECT_PATH)

execfile( ACTIVATE, dict(__file__=ACTIVATE) )

os.environ['DJANGO_SETTINGS_MODULE'] = 'inkscape.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

