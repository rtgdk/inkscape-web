from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _

DEFAULT_LANG = django_settings.LANGUAGE_CODE.split('-')[0]
OTHER_LANGS = list( i for i in django_settings.LANGUAGES if i[0].split('-')[0] != DEFAULT_LANG )

def get_setting(name, default):
    """
    A little helper for fetching global settings with a common prefix.
    """
    parent_name = "CMSPLUGIN_NEWS_{0}".format(name)
    return getattr(django_settings, parent_name, default)

"""
    Disables the latest news plugin
    Defaults to false
"""
DISABLE_LATEST_NEWS_PLUGIN = get_setting('DISABLE_LATEST_NEWS_PLUGIN', False)
FEED_SIZE = get_setting('FEED_SIZE', 10)
FEED_TITLE = get_setting('FEED_TITLE', _('News feed'))
FEED_DESCRIPTION = get_setting('FEED_DESCRIPTION', _('A feed full of news'))
ARCHIVE_PAGE_SIZE = get_setting('ARCHIVE_PAGE_SIZE', 15)
LINK_AS_ABSOLUTE_URL = get_setting('LINK_AS_ABSOLUTE_URL', True)
USE_LINK_ON_EMPTY_CONTENT_ONLY = get_setting('USE_LINK_ON_EMPTY_CONTENT_ONLY', True)
