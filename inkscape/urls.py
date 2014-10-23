from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from inkscape import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^doc/',       include('inkscape.docs.urls')),
    url(r'^',           include('django.contrib.staticfiles.urls')),
    url(r'^',           include('user_sessions.urls', 'user_sessions')),
    url(r'^',           include('social_auth.urls')),
)

urlpatterns += i18n_patterns('',
    url(r'^admin/',     include(admin.site.urls)),
    url(r'^project/',   include('inkscape.projects.urls')),
    url(r'^person/',    include('inkscape.person.urls')),
    url(r'^alerts/',    include('inkscape.alerts.urls')),
    url(r'^search/',    include('inkscape.search.urls')),
    url(r'^',           include('inkscape.resource.urls')),
    url(r'^',           include('cms.urls')),
)

if settings.DEBUG:
    import os
    admin_root = os.path.join(settings.STATIC_ROOT, '..', 'utils', 'admin-media')
    urlpatterns = patterns('django.views.static',
      # This urls will be covered over by apache
      (r'^admin/media/(?P<path>.*)$', 'serve', {'document_root': admin_root}),
      (r'^static/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),
      (r'^media/(?P<path>.*)$', 'serve', {'document_root': settings.MEDIA_ROOT}),
    ) + urlpatterns
