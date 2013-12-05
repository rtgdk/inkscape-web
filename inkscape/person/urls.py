try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from inkscape.person.views import *

urlpatterns = patterns('inkscape.person.views',
    url(r'^$',        'my_profile',      name='my_profile'),
    url(r'^(\d+)/$',  'view_profile',    name='view_profile'),
    url(r'^edit/$',   'edit_profile',    name='edit_profile'),
)
