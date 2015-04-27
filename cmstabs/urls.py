try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from .views import *

urlpatterns = patterns('inkscape.extra.views',
  url(r'^robots\.txt$',  'robots',       name='robots.txt'),
  url(r'^contact/us/$',  'contact_us',   name='contact'),
  url(r'^error/$',       'errors',       name='errors'),
)

