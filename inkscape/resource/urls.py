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
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from .views import *

def url_tree(regex, *urls):
    return url(regex, include(patterns('', *urls)))


urlpatterns = patterns('',
  url(r'^paste/(\d+)/','inkscape.resource.views.view_resource', name="pasted_item"),

  url_tree(r'^gallery/',
    url(r'^$',            GalleryList(),    name='galleries'),
    url(r'^me/$',         my_resources,     name='my_resources'),
    url(r'^trash/$',      view_trash,       name='trash'),
    url(r'^new/$',        edit_gallery,     name="new_gallery"),
    url(r'^paste/$',      paste_in,         name='pastebin'),

    url_tree(r'^(?P<gallery_id>\d+)/',
      url(r'^$',          view_gallery,     name="gallery"),
      url(r'^del/$',      delete_gallery,   name="delete_gallery"),
      url(r'^edit/$',     edit_gallery,     name='edit_gallery'),
      url(r'^add/$',      add_to_gallery,   name='add_to_gallery'),
      url(r'^new/$',      create_resource,  name='new_resource'),
      url(r'^icon/$',     gallery_icon,     name="gallery_icon"),
    ),

    url_tree(r'^item/(?P<item_id>\d+)/',
      url(r'^$',          view_resource,    name='resource'),
      url(r'^del/$',      delete_resource,  name='delete_resource'),
      url(r'^pub/$',      publish_resource, name='publish_resource'),
      url(r'^edit/$',     edit_resource,    name='edit_resource'),
      url(r'^download/$', down_resource,    name='download_resource', kwargs={'vt':'d'}),
      url(r'^view/$',     down_resource,    name='view_resource',     kwargs={'vt':'v'}),
      url(r'^(?P<like_id>[\+\-])$', like_resource, name='like'),
    ),

    url(r'^user/(?P<user_id>\d+)/$',                          view_user, name='user_resources'),
    url(r'^user/(?P<user_id>\d+)/flat/$',                     view_list, name='flat_resources'),
    url(r'^category/(?P<category_id>\d+)/$',                  view_list, name='resource_category'),
    url(r'^category/(?P<category_id>\d+)/(?P<user_id>\d+)/$', view_list, name='user_category'),
  ),
)

