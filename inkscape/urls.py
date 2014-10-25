from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^doc/',       include('inkscape.docs.urls')),
    url(r'^',           include('user_sessions.urls', 'user_sessions')),
    url(r'^',           include('social_auth.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns('',
    url(r'^admin/',     include(admin.site.urls)),
    url(r'^rosetta/',   include('rosetta.urls')),
    url(r'^project/',   include('inkscape.projects.urls')),
    url(r'^person/',    include('inkscape.person.urls')),
    url(r'^alerts/',    include('inkscape.alerts.urls')),
    url(r'^comments/',  include('django_comments.urls')),
    url(r'^search/',    include('inkscape.search.urls')),
    url(r'^',           include('inkscape.resource.urls')),
    url(r'^',           include('cms.urls')),
)

for e in ('403','404','500'):
    locals()['handler'+e] = 'views.error'+e
    urlpatterns += patterns('', url('^error/'+e+'/', 'views.error'+e, name='error'+e))

