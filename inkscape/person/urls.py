try:
    from django.conf.urls import patterns, url, include
except ImportError:
    from django.conf.urls.defaults import patterns, url, include

from django.views.generic.base import TemplateView

from registration.backends.default.views import ActivationView as AV, RegistrationView

from .forms import RegisForm, PasswordForm

def url_tree(regex, view='', *urls):
    return url(regex, include(patterns(view, *urls)))

AC = TemplateView.as_view(template_name='registration/activation_complete.html')
RC = TemplateView.as_view(template_name='registration/registration_complete.html')
RK = TemplateView.as_view(template_name='registration/registration_closed.html')
RG = RegistrationView.as_view(form_class=RegisForm)

urlpatterns = patterns('',
  url_tree(r'^user/', 'django.contrib.auth.views',
    url(r'^login/',     'login',                   name='auth_login'),
    url(r'^logout/',    'logout',                  name='auth_logout'),
    url(r'^pwd/$',      'password_reset', {'password_reset_form': PasswordForm }, name='password_reset'),
    url(r'^pwd/(?P<uidb64>.+?)/(?P<token>.+)/$', 'password_reset_confirm', name='password_reset_confirm'),
    url(r'^pwd/done/$', 'password_reset_complete', name='password_reset_complete'),
    url(r'^pwd/sent/$', 'password_reset_done',     name='password_reset_done'),

    url(r'^activate/complete/$',                AC,           name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$', AV.as_view(), name='registration_activate'),
    url(r'^register/$',                         RG,           name='auth_register'),
    url(r'^register/complete/$',                RC,           name='registration_complete'),
    url(r'^register/closed/$',                  RK,           name='registration_disallowed'),
    url(r'^register/',                          include('registration.auth_urls')),
  ),

  url_tree(r'', 'inkscape.person.views',
    url(r'^user/$',                   'my_profile',      name='my_profile'),
    url_tree(r'^~(?P<username>[\w-]+)', 'inkscape.person.views',
      url(r'^/?$',                    'view_profile',    name='view_profile'),
      url(r'^~/gpg/$',                'gpg_key',         name='user_gpgkey'),
    ),
    url(r'^edit/$',                   'edit_profile',    name='edit_profile'),
    url(r'^faces/$',                  'view_profiles',   name='faces'),
  ),
)
