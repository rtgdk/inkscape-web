from django.conf.urls.defaults import patterns, include
from inkscape import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'',              include('inkscape.content.urls', namespace='content')),
    (r'^news/',        include('inkscape.news.urls', namespace='news')),
    (r'^screenshots/', include('inkscape.screenshots.urls', namespace='screenshots')),
    (r'^admin/doc/',   include('django.contrib.admindocs.urls')),
    (r'^admin/',       include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('django.views.static',
      # This urls will be covered over by apache
      (r'^static/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_ROOT}),
      (r'^media/(?P<path>.*)$', 'serve', {'document_root': settings.MEDIA_ROOT}),
    )


urlpatterns += patterns('django.views.generic.simple',
    (r'^errors/403/', 'direct_to_template', {'template': '403.html'}),
    (r'^errors/404/', 'direct_to_template', {'template': '404.html'}),
    (r'^errors/500/', 'direct_to_template', {'template': '500.html'}),
)
