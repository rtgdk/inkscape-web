try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from inkscape.person.views import *

urlpatterns = patterns('inkscape.docs.views',
    url(r'^(.*)$',    'page',         name='doc'),
)
