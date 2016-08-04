#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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
from django.conf.urls import patterns, url, include
from .views import *

def url_tree(regex, *urls):
    return url(regex, include(patterns('', *urls)))

from person.urls import USER_URLS

USER_URLS.url_patterns.extend([
  # Example message system
  url(r'^/message/$',             CreateMessage.as_view(), name="message.new"),
  url(r'^/message/(?P<pk>\d+)/$', CreateMessage.as_view(), name="message.reply"),
])

urlpatterns = patterns('',
  url(r'^settings/$',                SettingsList.as_view(), name='alert.settings'),
  url(r'^view/',                     MarkAllViewed.as_view(), name="alert.view"),
  url(r'^delete/',                   MarkAllDeleted.as_view(), name='alert.delete'),

  url_tree(r'^(?P<pk>\d+)/',
    url(r'^view/',                   MarkViewed.as_view(), name="alert.view"),
    url(r'^delete/',                 MarkDeleted.as_view(), name='alert.delete'),
  ),

  url(r'^$',                         AlertList.as_view(), name="alerts"),
  url(r'^json/$',                    AlertsJson.as_view(), name="alerts.json"),
  url(r'^sent/$',                    SentMessages.as_view(), name="message.sent"),
  url_tree(r'^(?P<slug>[^\/]+)/',
    url(r'^$',                       AlertList.as_view(), name="alert.category"),
    url_tree(r'^subscribe/',
      url(r'^$',                     Subscribe.as_view(), name='alert.subscribe'),
      url(r'^(?P<pk>\d+)/$',         Subscribe.as_view(), name='alert.subscribe'),
    ),
    url_tree(r'^unsubscribe/',
      url(r'^$',                     Unsubscribe.as_view(), name='alert.unsubscribe'),
      url(r'^(?P<pk>\d+)/$',         Unsubscribe.as_view(), name='alert.unsubscribe'),
    ),
  ),
  url(r'^unsubscribe/(?P<pk>\d+)/$', Unsubscribe.as_view(), name='alert.unsubscribe'),
)

