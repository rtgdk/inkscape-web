try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from django.views.generic.base import TemplateView

from registration.backends.default.views import ActivationView as AV, RegistrationView

from .forms import RegisForm


urlpatterns = patterns('django.contrib.auth.views',
    url(r'^login/',     'login',                name='auth_login'          ),
    url(r'^logout/',    'logout',               name='auth_logout'         ),
    url(r'^pwd/$',      'password_change',      name='password_change'     ),
    url(r'^pwd/y/$',    'password_change_done', name='password_change_done'),
)

AC = TemplateView.as_view(template_name='registration/activation_complete.html')
RC = TemplateView.as_view(template_name='registration/registration_complete.html')
RK = TemplateView.as_view(template_name='registration/registration_closed.html')
RG = RegistrationView.as_view(form_class=RegisForm)

urlpatterns += patterns('',
    url(r'^activate/complete/$',                AC,           name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$', AV.as_view(), name='registration_activate'),
    url(r'^register/$',                         RG,           name='registration_register'),
    url(r'^register/complete/$',                RC,           name='registration_complete'),
    url(r'^register/closed/$',                  RK,           name='registration_disallowed'),
    url(r'^register/',                          include('registration.auth_urls')),
)

urlpatterns += patterns('inkscape.person.views',
    url(r'^$',        'my_profile',      name='my_profile'),
    url(r'^edit/$',   'edit_profile',    name='edit_profile'),
    url(r'^faces/$',  'view_profiles',   name='faces'),
    url(r'^contact/$','contact_us',      name='contact'),
    url(r'^(?P<username>[\w-]+)/$', 'view_profile', name='view_profile'),
)
