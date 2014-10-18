

import os
import sys
import email
import django
import logging

from django.conf import settings
from os.path import join, dirname

def get_versions(project_dir):
    """return the bzr revision number and version of the project"""

    version_file = os.path.join(project_dir, 'version')
    if not os.path.exists(version_file):
        return ("E?", "E?")

    emai_msg = email.message_from_file(open(version_file))
    return (emai_msg["version"], emai_msg["inkscape"])


def bzr_revision():
    try:
        with open(join(dirname(dirname(__file__)), '.bzr', 'branch', 'last-revision')) as rev:
            return rev.read().split()[0]
    except:
        return ''


# Freeze this as it is now.
code_revision = bzr_revision()


def versions_context_processor(request):
    return {'INKSCAPE_VERSION': settings.INKSCAPE_VERSION,
            'CODE_VERSION': code_revision,
            'CONTENT_VERSION': bzr_revision(),
            'DJANGO_VERSION': django.get_version(),
            'PYTHON_VERSION': sys.version.split()[0]
            }
