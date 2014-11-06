try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from .views import *

urlpatterns = patterns('',
    url(r'^contact-admin/', contact_us, name='contact'),
    url(r'^moderation/$', Moderation.as_view(), name="moderation"),
    url(r'^moderation/flagged$', ModerateFlagged.as_view(), name="moderate_flagged"),
)
