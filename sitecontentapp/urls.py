from django.conf.urls.defaults import *

urlpatterns = patterns('django.views.generic.simple',
    (r'^$',         'direct_to_template', {'template': 'front.html'}),
    #(r'^download$', 'direct_to_template', {'template': 'download.html'}),
)


def redirect(from_, to):
    return (from_, 'redirect_to', {'url': to})


urlpatterns += patterns('django.views.generic.simple',
    # Possibly common mistakes
    redirect(r'^downloads/?$',      '/download/'),
    redirect(r'^downloads/$',       '/download/'),
    redirect(r'^download$',         '/download/'),

    # Legacy
    redirect(r'^download.php$',     '/download/'),
    redirect(r'^about/overview/?$', '/about'),
    redirect(r'^doc/inkscape-man.html$',
        'http://inkscape.modevia.com/inkscape-man.html'),
    redirect(r'^planet/?$',          'http://planet.inkscape.org/'),
    redirect(r'^(FAQ|help|HELP)/?$', '/faq'),

    redirect(r'^favicon.ico$', '/media/favicon.ico'),
)

urlpatterns += patterns('',
    (r'(?P<url>.*)', 'sitecontentapp.views.load_page'),
)
