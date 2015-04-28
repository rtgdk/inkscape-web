
import os
import sys
import email
import django
import logging

from django.conf import settings

def design(request):
    """
    Adds static-related context variables to the context.
    """
    return {
      'DEBUG': settings.DEBUG,
      'GOOGLE_ANID': settings.GOOGLE_ANID,
    }

INKSCAPE_VERSION = ''
WEBSITE_VERSION = ''
WEBSITE_REVISION = ''

VERSION_FILE = os.path.join(settings.PROJECT_PATH, 'version')
if os.path.exists(VERSION_FILE):
    emai_msg = email.message_from_file(open(VERSION_FILE))
    WEBSITE_VERSION = emai_msg["version"]
    INKSCAPE_VERSION = emai_msg["inkscape"]

REVISION_FILE = os.path.join(settings.PROJECT_PATH, 'data', 'revision')
if os.path.isfile(REVISION_FILE):
    with open(REVISION_FILE, 'r') as fhl:
        REVISION = fhl.read().strip()

def version(request):
    return {
      'INKSCAPE_VERSION': INKSCAPE_VERSION,
      'WEBSITE_REVISION': WEBSITE_REVISION,
      'WEBSITE_VERSION': WEBSITE_VERSION,
      'DJANGO_VERSION': django.get_version(),
      'PYTHON_VERSION': sys.version.split()[0]
    }

