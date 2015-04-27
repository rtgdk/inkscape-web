
try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from .views import *

def url_tree(regex, *urls):
    return url(regex, include(patterns('', *urls)))

urlpatterns = patterns('',
  url(r'^$',                   Moderation(),      name="moderation"),

  url_tree(r'^(?P<app>[\w-]+)/(?P<name>[\w-]+)/',
    url(r'^flagged/$',         ModerateFlagged(), name="moderation.flagged"),
    url(r'^latest/$',          ModerateLatest(),  name="moderation.latest"),

    url_tree(r'^(?P<pk>\d+)/',
      url(r'^$',               FlagObject(),      name='moderation.flag'),
      url(r'^hide/$',          HideComment(),     name="moderation.hide"),
      url(r'^approve/$',       ApproveComment(),  name="moderation.approve"),
    )
  )
)
