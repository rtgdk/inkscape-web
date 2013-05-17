#!/usr/bin/python

import os
import sys

CODE_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.abspath(os.path.join(CODE_PATH, ".."))
#PROJECT_PATH = '/var/www/staging.inkscape.org' <- Why is this required?
ACTIVATE = os.path.join(PROJECT_PATH, 'pythonenv/bin/activate_this.py')

sys.path.insert(0, PROJECT_PATH)

execfile( ACTIVATE, dict(__file__=ACTIVATE) )

os.environ['DJANGO_SETTINGS_MODULE'] = 'inkscape.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

