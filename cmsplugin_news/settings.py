#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#

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
