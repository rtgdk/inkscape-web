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

from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from .views import SearchView

urlpatterns = patterns('',
    url(r'^', include('social_auth.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns('inkscape.views',
    url(r'^robots\.txt$',  'robots',       name='robots.txt'),
    url(r'^contact/us/$',  'contact_us',   name='contact'),
    url(r'^search/$',      SearchView(),   name='search'),
    url(r'^error/$',       'errors',       name='errors'),

    url(r'^admin/lookups/', include('ajax_select.urls')),
    url(r'^admin/',     include(admin.site.urls)),
    #url(r'^tr/',        include('cmsrosetta.urls')),
    url(r'^doc/',       include('docs.urls')),
    url(r'^project/',   include('projects.urls')),
    url(r'^release/',   include('releases.urls')),
    url(r'^alerts/',    include('alerts.urls')),
    url(r'^comments/',  include('django_comments.urls')),
    url(r'^cms/',       include('cmsdiff.urls')),
    url(r'^moderation/',include('moderation.urls')),
    url(r'^news/',      include('cmsplugin_news.urls')),
    url(r'^',           include('person.urls')),
    url(r'^',           include('resource.urls')),
    url(r'^',           include('cms.urls')),
)

for e in ('403','404','500'):
    locals()['handler'+e] = 'inkscape.views.error' + e
    urlpatterns += patterns('inkscape.views',
        url('^error/' + e + '/$', 'error' + e, name='error' + e))
