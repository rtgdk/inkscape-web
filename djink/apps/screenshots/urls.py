from django.conf.urls.defaults import patterns
from .views import screenshots

urlpatterns = patterns('',
        (r'^screenshots/gallery/(?P<file>.*\.png)$',
            'django.views.generic.simple.redirect_to',
            {'url': '/media/images/screenshots/%(file)s'}),
        (r'^((?P<version>.*)/)?$', screenshots),
)

