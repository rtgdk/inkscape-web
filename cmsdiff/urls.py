"""
Provides views for the cms diff functionality.
"""

from django.conf.urls import patterns, url
from .views import ViewDiff

urlpatterns = patterns('',
   url(r'^diff/(?P<pk>\d+)/$', ViewDiff.as_view(), name='cms.diff'),
)
