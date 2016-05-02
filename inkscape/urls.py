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

from .views import *

from cms import appresolver
old = appresolver.get_app_patterns
def get_app_patterns(*args, **kwargs):
    try:
        return old(*args, **kwargs)
    except:
        return []
appresolver.get_app_patterns = get_app_patterns

urlpatterns = patterns('',
  url(r'^', include('social.apps.django_app.urls', namespace='social')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns('inkscape.views',
    url(r'^robots\.txt$',  Robots.as_view(), name='robots.txt'),
    url(r'^contact/us/$',  ContactUs.as_view(), name='contact'),
    url(r'^contact/ok/$',  ContactOk.as_view(), name='contact.ok'),
    url(r'^search/$',      SearchView(), name='search'),
    url(r'^error/$',       Errors.as_view(), name='errors'),
    url(r'^credits/$',     Authors.as_view(), name='authors'),

    url(r'^admin/lookups/', include('ajax_select.urls')),
    url(r'^admin/',     include(admin.site.urls)),
    #url(r'^tr/',        include('cmsrosetta.urls')),
    url(r'^doc/',       include('docs.urls')),
    url(r'^projects/',   include('projects.urls')),
    url(r'^release/',   include('releases.urls')),
    url(r'^alerts/',    include('alerts.urls')),
    url(r'^comments/',  include('django_comments.urls')),
    url(r'^cms/',       include('cmsdiff.urls')),
    url(r'^moderation/',include('moderation.urls')),
    url(r'^news/',      include('cmsplugin_news.urls', namespace='news')),
    url(r'^logs/',      include('logbook.urls', namespace='logbook')),
    url(r'^',           include('person.urls')),
    url(r'^',           include('resources.urls')),
    url(r'^',           include('cms.urls')),
)

for e in ('403','404','500'):
    locals()['handler'+e] = Error.as_error(e)
    urlpatterns += patterns('', url('^error/%s/$' % e, Error.as_error(e)))
