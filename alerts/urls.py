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
try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from .views import *

def url_tree(regex, *urls):
    return url(regex, include(patterns('', *urls)))

from person.urls import USER_URLS

USER_URLS.url_patterns.extend([
  # Example message system
  url(r'^/message/$', CreateMessage(), name="message.new"),
  url(r'^/sent/$',    SentMessages(), name="message.sent"),
])

urlpatterns = patterns('',
  url(r'^settings/$',                SettingsList(),  name='alert.settings'),
  url(r'^unsubscribe/(?P<pk>\d+)/$', unsubscribe,     name='alert.unsubscribe'),

  url_tree(r'^(?P<alert_id>\d+)/',
    url(r'^view/',   mark_viewed,     name="alert.view"),
    url(r'^delete/', mark_deleted,    name='alert.delete'),
  ),

  url(r'^$',                  AlertList(), name="alerts"),
  url_tree(r'^(?P<slug>[^\/]+)/',
    url(r'^$',                AlertList(), name="alerts"),
    url_tree(r'subscribe/',
      url(r'^$',              Subscribe(), name='alert.subscribe'),
      url(r'^(?P<pk>\d+)/$',  Subscribe(), name='alert.subscribe'),
    ),
  ),

)

