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

from django.conf.urls import *

from .feeds import *
from .views import *

def url_tree(regex, *urls):
    return url(regex, include(patterns('', *urls)))

urlpatterns = patterns('django.views.generic.date_based',
    url(r'^$',             ArchiveIndexView.as_view(), name='archive_index'),
    url(r'^feed/$',        NewsFeed(),                 name='rss'),

    url_tree(r'^(?P<year>\d{4})/',
      url(r'^$',                      YearArchiveView.as_view(),  name='archive_year'),
      url_tree(r'^(?P<month>\d{2})/',
        url(r'^$',                    MonthArchiveView.as_view(), name='archive_month'),
        url_tree(r'^(?P<day>\d{2})/',
          url(r'^$',                  DayArchiveView.as_view(),   name='archive_day'),
          url(r'^(?P<slug>[-\w]+)/$', DetailView.as_view(),       name='detail'),
        ),
      ),
    ),

    url(r'^unpublished/(?P<pk>\d+)/$', DetailNews.as_view(),       name="item"),
)
