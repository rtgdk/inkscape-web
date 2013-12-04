from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _
import os

def get_setting(name, default):
    """Helper for fetching global settings with a common prefix"""
    parent_name = "CMSPLUGIN_LAUNCHPAD_{0}".format(name)
    return getattr(django_settings, parent_name, default)

_TM = (
    ('launchpad/list.html', 'Listing'),
    ('launchpad/count.html', 'Simple Count'),
)

LP_TEMPLATES = get_setting('TEMPLATES', _TM )

