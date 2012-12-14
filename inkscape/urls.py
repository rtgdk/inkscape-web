from django.conf.urls.defaults import patterns, include

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^404', 'django.views.generic.simple.direct_to_template', {'template':
        'fake-404.html'}),
    (r'^/*(?P<url>/.*)', 'django.views.generic.simple.redirect_to'),
)

import settings
if settings.DEBUG:
    from django.views.static import serve
    _media_url = settings.MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('',
                                (r'^%s(?P<path>.*)$' % _media_url,
                                serve,
                                {'document_root': settings.MEDIA_ROOT}))
    del _media_url, serve

    urlpatterns += patterns('django.views.generic.simple',
            (r'^errors/403/', 'direct_to_template', {'template': '403.html'}),
            (r'^errors/404/', 'direct_to_template', {'template': '404.html'}),
            (r'^errors/500/', 'direct_to_template', {'template': '500.html'}))


urlpatterns += patterns('',
    (r'^news/', include('inkscape.apps.news.urls', namespace='news')),
    (r'^screenshots/', include('inkscape.apps.screenshots.urls', namespace='screenshots')),
    (r'', include('inkscape.apps.content.urls', namespace='content')),
)
