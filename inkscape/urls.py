from django.conf.urls.defaults import patterns, include, url
from inkscape import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/',   include('django.contrib.admindocs.urls')),
    (r'^admin/',       include(admin.site.urls)),
    url(r'^auth/login/',   'django.contrib.auth.views.login', name='auth_login'),
    url(r'^auth/logout/',  'django.contrib.auth.views.logout',{'next_page': '/'}, name='auth_logout'),
    url(r'^auth/',     include('registration.backends.default.urls')),
    (r'^',             include('social_auth.urls')),
    (r'^',             include('cms.urls')),
    (r'^',             include('django.contrib.staticfiles.urls')),
)

if settings.DEBUG:
    urlpatterns = patterns('django.views.static',
      # This urls will be covered over by apache
      (r'^design/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),
      (r'^media/(?P<path>.*)$', 'serve', {'document_root': settings.MEDIA_ROOT}),
    ) + urlpatterns


urlpatterns += patterns('django.views.generic.simple',
    (r'^errors/403/', 'direct_to_template', {'template': 'error/403.html'}),
    (r'^errors/404/', 'direct_to_template', {'template': 'error/404.html'}),
    (r'^errors/500/', 'direct_to_template', {'template': 'error/500.html'}),
)
