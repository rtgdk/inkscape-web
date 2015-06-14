# -*- coding: utf-8 -*-
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
from django.conf.urls import patterns, url, include

from .views import *

def url_tree(regex, *urls):
    return url(regex, include(patterns('', *urls)))

from person.urls import USER_URLS, TEAM_URLS

owner_patterns = [
  url_tree(r'^/gallery/',
    url(r'^$',                                            GalleryList(), name='resources'),
    url(r'^rss/$',                                        GalleryFeed(), name='resources_rss'),
    url(r'^(?P<galleries>[^\/]+)/$',                      GalleryList(), name='resources'),
    url(r'^(?P<galleries>[^\/]+)/rss/$',                  GalleryFeed(), name='resources_rss'),
    url(r'^all/(?P<category>[^\/]+)/$',                   GalleryList(), name='resources'),
    url(r'^all/(?P<category>[^\/]+)/rss/$',               GalleryFeed(), name='resources_rss'),
    url(r'^(?P<galleries>[^\/]+)/(?P<category>[^\/]+)/$', GalleryList(), name='resources'),
    url(r'^(?P<galleries>[^\/]+)/(?P<category>[^\/]+)/rss/$', GalleryFeed(), name='resources_rss'),
  ),
  # Try a utf-8 url, see if it breaks web browsers.
  url(r'^/★(?P<slug>[^\/]+)$'.decode('utf-8'),            ViewResource(), name='resource'),
]
# Add to the username user profile and teamname
USER_URLS.url_patterns.extend(owner_patterns)
TEAM_URLS.url_patterns.extend(owner_patterns)

urlpatterns = patterns('',
  url(r'^paste/(?P<pk>\d+)/$',        ViewResource(),   name='pasted_item'),

  url_tree('^mirror/',
    url(r'^$',                        mirror_resources, name='mirror'),
    url(r'^add/$',                    MirrorAdd(),      name='mirror.add'),
    url_tree(r'^(?P<uuid>[\w-]+)/',
      url(r'^$',                      mirror_resources, name='mirror'),
      url(r'^file/(?P<filename>.+)$', mirror_resource,  name="mirror.item"),
    ),
  ),

  url_tree(r'^gallery/',
    url(r'^$',             GalleryList(),    name='resources'),
    url(r'^rss/$',         GalleryFeed(),    name='resources_rss'),
    url(r'^new/$',         CreateGallery(),  name='new_gallery'),
    url(r'^paste/$',       PasteIn(),        name='pastebin'),
    url(r'^upload/$',      UploadResource(), name='resource.upload'),
    url(r'^upload/go/$',   DropResource(),   name='resource.drop'),

    url_tree(r'^(?P<gallery_id>\d+)/',
      url(r'^del/$',       DeleteGallery(),  name='gallery.delete'),
      url(r'^edit/$',      EditGallery(),    name='gallery.edit'),
      url(r'^upload/$',    UploadResource(), name='resource.upload'),
      url(r'^upload/go/$', DropResource(),   name='resource.drop'),
    ),

    url_tree(r'^item/(?P<pk>\d+)/',
      url(r'^$',           ViewResource(),      name='resource'),
      url(r'^del/$',       DeleteResource(),    name='delete_resource'),
      url(r'^pub/$',       PublishResource(),   name='publish_resource'),
      url(r'^edit/$',      EditResource(),      name='edit_resource'),
      url(r'^view/$',      DownloadResource(),  name='view_resource'),
      url(r'^move/$',      MoveResource(),      name='resource.move'),
      url(r'^copy/$',      MoveResource(),      name='resource.copy'),
      url(r'^readme.txt$', down_readme,         name='resource.readme'),
      url(r'^(?P<like>[\+\-])$', like_resource, name='resource.like'),
      url(r'^(?P<fn>.+)$', DownloadResource(),  name='download_resource'),
    ),

    url(r'^(?P<category>[^\/]+)/$',     GalleryList(), name='resources'),
    url(r'^(?P<category>[^\/]+)/rss/$', GalleryFeed(), name='resources_rss'),
  ),
)

