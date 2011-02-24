from django.conf.urls.defaults import patterns
from . import views

urlpatterns = patterns('',
    (r'^$', views.archive_all),
    (r'^(?P<year>\d+)/$', views.archive_year),
    (r'^(?P<year>\d+)/(?P<slug>[\w.-]+)/$', views.article),
    (r'^category/(?P<slug>[\w.-]+)/$', views.category),
)

