try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from inkscape.search.views import SearchView

urlpatterns = patterns('inkscape.search.views',
    url(r'^$', SearchView(), name='haystack_search'),
)
