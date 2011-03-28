import sys
from os.path import join, dirname
from django.conf import settings
import django


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
