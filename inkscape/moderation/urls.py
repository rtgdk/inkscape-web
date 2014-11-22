
try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from .views import *

urlpatterns = patterns('',
    url(r'^$',                  Moderation(),      name="moderation"),
    url(r'^flagged/$',          ModerateFlagged(), name="moderate_flagged"),
    url(r'^latest/$',           ModerateLatest(),  name="moderate_latest"),
    url(r'^hide/(?P<pk>\d+)/$', HideComment(),     name="hide_comment"),
)
