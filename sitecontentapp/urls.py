from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
    (r'^$',         'direct_to_template', {'template': 'front.html'}),
    #(r'^download$', 'direct_to_template', {'template': 'download.html'}),
)

urlpatterns += patterns('django.views.generic.simple',
    (r'^download.php$', 'redirect_to', {'url': '/download'}),
    (r'^downloads$',    'redirect_to', {'url': '/download'}),
    (r'^downloads/$',   'redirect_to', {'url': '/download'}),
    (r'^download/$',    'redirect_to', {'url': '/download'}),
)

urlpatterns += patterns('',
    (r'(?P<url>.*)', 'sitecontentapp.views.load_page'),
)
