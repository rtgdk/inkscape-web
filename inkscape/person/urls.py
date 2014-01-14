try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from inkscape.person.views import *
from registration.backends.default.views import ActivationView as AV, RegistrationView as RV

urlpatterns = patterns('inkscape.person.views',
    url(r'^$',        'my_profile',      name='my_profile'),
    url(r'^(\d+)/$',  'view_profile',    name='view_profile'),
    url(r'^edit/$',   'edit_profile',    name='edit_profile'),
    url(r'^faces/$',  'view_profiles',   name='faces'),

    url(r'^register/$',       'register', name='registration_register'),
    url(r'^register/(\w+)/$', 'register', name='registration_activate'),
    url(r'^register/(y)/$',   'register', name='registration_complete'),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login/',   'login',                name='auth_login'          ),
    url(r'^logout/',  'logout',               name='auth_logout'         ),
    url(r'^pwd/$',    'password_change',      name='password_change'     ),
    url(r'^pwd/y/$',  'password_change_done', name="password_change_done"),
)


