from django.conf.urls.defaults import patterns, url
from .views import load_page

urlpatterns = patterns('django.views.generic.simple',
    (r'^$',         'direct_to_template', {'template': 'front.html'}),
    #(r'^download$', 'direct_to_template', {'template': 'download.html'}),
)


def redirect(from_, to):
    return (from_, 'redirect_to', {'url': to})


# Groups must be named or be (?:) to avoid a TypeError on multiple values for kwarg url
urlpatterns += patterns('django.views.generic.simple',
    # Nice
    redirect(r'^downloads/$',      '/download/'),
    redirect(r'^about/overview/$', '/about/'),

    # Legacy
    redirect(r'^screenshots/gallery/(?P<file>.*\.png)$', '/media/images/screenshots/%(file)s'),
    redirect(r'^books/(?:index.php)?$', '/learn/books/'),
    redirect(r'^download.php$',     '/download/'),
    redirect(r'^doc/inkscape-man.html$',
        'http://inkscape.modevia.com/inkscape-man.html'),
    redirect(r'^planet/?$',          'http://planet.inkscape.org/'),
    redirect(r'^(?:FAQ|help|HELP)/?$', '/faq'),

    redirect(r'^favicon.ico$', '/media/favicon.ico'),
    redirect(r'^showcase/web_design/(?:index.php)?$', '/showcase/web-design/'),
    redirect(r'^(?P<dir>.*/)index.php$', '/%(dir)s'),
)

urlpatterns += patterns('',
    url(r'^users/(?P<url>.*)/$', load_page, {'prefix': 'users/'},
        name='users'),
    (r'(?P<url>.*)/$', load_page),
)
