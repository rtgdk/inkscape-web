from django.conf.urls.defaults import patterns, url
from . import views
from .feeds import LatestNewsFeed

urlpatterns = patterns('',
    url(r'^$', views.archive_all, name='all'),
    url(r'^(?P<year>\d+)/$', views.archive_year, name='year'),
    url(r'^(?P<year>\d+)/(?P<slug>[\w.-]+)/$', views.article, name='article'),
    url(r'^category/(?P<slug>[\w.-]+)/$', views.category, name='category'),
    url(r'^rss/$', LatestNewsFeed(), name='rss'),
)

