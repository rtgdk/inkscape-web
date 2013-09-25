from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _
import os

def get_setting(name, default):
    """Helper for fetching global settings with a common prefix"""
    parent_name = "CMSPLUGIN_BROCHURE_{0}".format(name)
    return getattr(django_settings, parent_name, default)

FEED_SIZE = get_setting('FEED_SIZE', 50)
MEDIA_ROOT = get_setting('MEIDA',
    os.path.join(django_settings.MEDIA_ROOT, 'brochure'))

