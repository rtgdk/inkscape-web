#!/usr/bin/python

import os
import sys

CODE_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.abspath(os.path.join(CODE_PATH, ".."))

sys.path.insert(0, PROJECT_PATH)

print PROJECT_PATH

os.environ['DJANGO_SETTINGS_MODULE'] = 'inkscape.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()


