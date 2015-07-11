#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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

urlpatterns = patterns('',
  url(r'^$',                   Moderation(),      name="moderation"),

  url_tree(r'^(?P<app>[\w-]+)/(?P<name>[\w-]+)/',
    url(r'^flagged/$',         ModerateFlagged(), name="moderation.flagged"),
    url(r'^latest/$',          ModerateLatest(),  name="moderation.latest"),

    url_tree(r'^(?P<pk>\d+)/',
      url(r'^$',               FlagObject(),      name='moderation.flag'),
      url(r'^hide/$',          HideComment(),     name="moderation.hide"),
      url(r'^approve/$',       ApproveComment(),  name="moderation.approve"),
    )
  )
)
