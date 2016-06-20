"""
Provides views for the cms diff functionality.
"""
from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('',
   url(r'^diff/$', DiffView.as_view(), name='cms.diff'),
   url(r'^diff/(?P<pk>\d+)/$', DiffRedirect.as_view(), name='cms.diff')
)
