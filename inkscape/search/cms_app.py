try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp

from inkscape.search.views import SearchView
from haystack.views import search_view_factory

class SearchApphook(CMSApp):
    name = _("search apphook")
    urls = [patterns('',
        url('^$', search_view_factory(SearchView), name='search'),
    ),]

