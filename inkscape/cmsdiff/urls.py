try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from .views import *

urlpatterns = patterns('',
   url(r'^diff/(?P<pk>\d+)/$', ViewDiff(), name='cms.diff'),
)
