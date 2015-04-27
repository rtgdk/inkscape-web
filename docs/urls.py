try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('docs.views',
    url(r'^(.*)$', 'page', name='doc'),
)
