from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from inkscape import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/',   include('django.contrib.admindocs.urls')),
    (r'^admin/',       include(admin.site.urls)),
    url(r'^auth/login/',   'django.contrib.auth.views.login', name='auth_login'),
    url(r'^auth/logout/',  'django.contrib.auth.views.logout',{'next_page': '/'}, name='auth_logout'),
    url(r'^auth/',     include('registration.backends.default.urls')),
    url(r'^person/',   include('inkscape.person.urls')),
    (r'^',             include('social_auth.urls')),
    (r'^',             include('django.contrib.staticfiles.urls')),
)

urlpatterns += i18n_patterns('',
    (r'^',             include('cms.urls')),
)

if settings.DEBUG:
    import os
    admin_root = os.path.join(settings.STATIC_ROOT, '..', 'utils', 'admin-media')
    urlpatterns = patterns('django.views.static',
      # This urls will be covered over by apache
      (r'^admin/media/(?P<path>.*)$', 'serve', {'document_root': admin_root}),
      (r'^design/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),
      (r'^media/(?P<path>.*)$', 'serve', {'document_root': settings.MEDIA_ROOT}),
    ) + urlpatterns
