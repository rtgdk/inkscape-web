#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
"""
Urls for logbook
"""

from django.conf.urls import patterns, url, include

from .views import RequestStats, MetricList, MetricDetails

def url_tree(regex, *urls):
    """Convience function for url trees"""
    return url(regex, include(patterns('', *urls)))

urlpatterns = patterns('',
  url(r'^$',                     MetricList.as_view(), name="metrics"),
  url_tree(r'^_(?P<path>[^/]+)/',
    url('^$',                    RequestStats.as_view(), name="request"),
  ),
  url_tree(r'^(?P<slug>\w+)/',
    url(r'^$',                   MetricDetails.as_view(), name="metric"),
  ),
)

