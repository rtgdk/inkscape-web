from django.conf.urls.defaults import *
from .views import load_page

urlpatterns = patterns('django.views.generic.simple',
    (r'^$',         'direct_to_template', {'template': 'front.html'}),
    #(r'^download$', 'direct_to_template', {'template': 'download.html'}),
)


def redirect(from_, to):
    return (from_, 'redirect_to', {'url': to})


urlpatterns += patterns('django.views.generic.simple',
    # Nice
    redirect(r'^downloads/$',      '/download/'),
    redirect(r'^about/overview/$', '/about/'),

    # Legacy
    redirect(r'^books/(index.php)?$', '/learn/books/'),
    redirect(r'^download.php$',     '/download/'),
    redirect(r'^doc/inkscape-man.html$',
        'http://inkscape.modevia.com/inkscape-man.html'),
    redirect(r'^planet/?$',          'http://planet.inkscape.org/'),
    redirect(r'^(FAQ|help|HELP)/?$', '/faq'),

    redirect(r'^favicon.ico$', '/media/favicon.ico'),
)

urlpatterns += patterns('',
    url(r'^users/(?P<url>.*)/$', load_page, {'prefix': 'users/'},
        name='users'),
    (r'(?P<url>.*)/$', load_page),
)
