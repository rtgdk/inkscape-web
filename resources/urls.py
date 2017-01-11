# -*- coding: utf-8 -*-
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

from person.urls import USER_URLS, TEAM_URLS

def resource_search(*args, **kw):
    """Generate standard url patterns for resource listing"""
    return [
      url(r'^$',               kw.get('rl', ResourceList)(), name='resources'),
      url(r'^pick/$',          kw.get('rp', ResourcePick)(), name='resources_pick'),
      url(r'^rss/$',           kw.get('rf', ResourceFeed)(), name='resources_rss'),
      url_tree(r'^=(?P<category>[^\/]+)/',
        url(r'^$',             kw.get('rl', ResourceList)(), name='resources'),
        url(r'^rss/$',         kw.get('rf', ResourceFeed)(), name='resources_rss'),
        *args)
    ]

owner_patterns = [
  url_tree(r'^/galleries/',
    url(r'^$', GalleryList(), name='galleries'),
    url_tree(r'^(?P<galleries>[^\/]+)/', *resource_search(rl=GalleryView)),
  ),
  url_tree(r'^/resources/', *resource_search()),
]
user_patterns = [
  # Try a utf-8 url, see if it breaks web browsers.
  url(r'^/★(?P<slug>[^\/]+)$'.decode('utf-8'), ViewResource(), name='resource'),
]
# Add to the username user profile and teamname
USER_URLS.url_patterns.extend(owner_patterns + user_patterns)
TEAM_URLS.url_patterns.extend(owner_patterns)

urlpatterns = patterns('',
  url(r'^paste/(?P<pk>\d+)/$',            ViewResource(),   name='pasted_item'),
  url(r'^json/tags.json$',                TagsJson(),       name='tags.json'),

  url_tree('^mirror/',
    url(r'^$',                            MirrorIndex(),    name='mirror'),
    url(r'^add/$',                        MirrorAdd(),      name='mirror.add'),
    url_tree(r'^(?P<slug>[\w-]+)/',
      url(r'^$',                          MirrorView(),     name='mirror'),
      url(r'^file/(?P<filename>[^\/]+)$', MirrorResource(), name="mirror.item"),
    ),
  ),
  
  url_tree(r'^gallery/',
    url(r'^new/$',         CreateGallery(),  name='new_gallery'),
    url(r'^paste/$',       PasteIn(),        name='pastebin'),
    url(r'^upload/$',      UploadResource(), name='resource.upload'),
    url(r'^upload/go/$',   DropResource(),   name='resource.drop'),
    url(r'^link/$',        LinkToResource(), name='resource.link'),

    url_tree(r'^(?P<gallery_id>\d+)/',
      # We should move these to galleries/
      url(r'^del/$',       DeleteGallery(),  name='gallery.delete'),
      url(r'^edit/$',      EditGallery(),    name='gallery.edit'),
      url(r'^upload/$',    UploadResource(), name='resource.upload'),
      url(r'^upload/go/$', DropResource(),   name='resource.drop'),
      url(r'^link/$',      LinkToResource(), name='resource.link'),
    ),

    url_tree(r'^item/(?P<pk>\d+)/',
      url(r'^$',                 ViewResource(),      name='resource'),
      url(r'^del/$',             DeleteResource(),    name='delete_resource'),
      url(r'^pub/$',             PublishResource(),   name='publish_resource'),
      url(r'^edit/$',            EditResource(),      name='edit_resource'),
      url(r'^view/$',            DownloadResource(),  name='view_resource'),
      url(r'^move/(?P<source>\d+)/$', MoveResource(), name='resource.move'),
      url(r'^copy/$',            MoveResource(),      name='resource.copy'),
      url(r'^readme.txt$',       down_readme,         name='resource.readme'),
      url(r'^(?P<like>[\+\-])$', VoteResource.as_view(), name='resource.like'),
      url(r'^(?P<fn>[^\/]+)/?$', DownloadResource(),  name='download_resource'),
    ),
    *resource_search(
        url(r'^(?P<galleries>[^\/]+)/',     GalleryView(),  name='resources'),
        url(r'^(?P<galleries>[^\/]+)/rss/', ResourceFeed(), name='resources_rss'),
    )
  ),
)

