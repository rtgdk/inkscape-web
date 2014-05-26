#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from .views import *

urlpatterns = patterns('',
    url(r'^$',                    my_resources,    name='my_resources'),

    url(r'^item/(\d+)/$',         view_resource,   name='resource'),
    url(r'^item/(\d+)/del/$',     delete_resource, name='delete_resource'),
    url(r'^item/(\d+)/del/(y)/$', delete_resource, name='yes_delete_resource'),
    url(r'^item/(\d+)/edit/$',    edit_resource,   name='edit_resource'),
    url(r'^item/new/$',           edit_resource,   name='new_resource'),

    url(r'^user/(\w+)/$',         view_user,       name='user_resources'),

    url(r'^gallery/(\d+)/$',         view_gallery,   name="gallery"),
    url(r'^gallery/(\d+)/del/$',     delete_gallery, name="delete_gallery"),
    url(r'^gallery/(\d+)/del/(y)/$', delete_gallery, name='yes_delete_gallery'),
    url(r'^gallery/(\d+)/edit/$',    edit_gallery,   name='edit_gallery'),
    url(r'^gallery/(\d+)/add/$',     add_to_gallery, name='add_to_gallery'),
    url(r'^gallery/new/$',           edit_gallery,   name="new_gallery"),

    url(r'^cat/(\w+)/$',             view_category,   name='category_resources'),
)

