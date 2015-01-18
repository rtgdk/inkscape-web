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
UIDB = r'^(?P<uidb64>.+?)/(?P<token>.+)/$'

# Our user url implemination allows other urls files to add
# their own urls to our user tree. Creating user functions.
USER_URLS = url_tree(r'^~(?P<username>[^\/]+)', 'inkscape.person.views',
  url(r'^/?$',                    'view_profile',    name='view_profile'),
  url(r'^/gpg/$',                 'gpg_key',         name='user_gpgkey'),
)
add_user_url = USER_URLS.url_patterns.append

urlpatterns = patterns('',
  url_tree(r'^user/', 'django.contrib.auth.views',
    url(r'^login/',     'login',                 name='auth_login'),
    url(r'^logout/',    'logout',                name='auth_logout'),
    url_tree(r'^pwd/', 'django.contrib.auth.views',
      url(r'^$',      'password_reset', {'password_reset_form': PasswordForm }, name='password_reset'),
      url(UIDB,       'password_reset_confirm',  name='password_reset_confirm'),
      url(r'^done/$', 'password_reset_complete', name='password_reset_complete'),
      url(r'^sent/$', 'password_reset_done',     name='password_reset_done'),
    ),

    url_tree(r'^register/', '',
      url(r'^$',                         RG,           name='auth_register'),
      url(r'^complete/$',                RC,           name='registration_complete'),
      url(r'^closed/$',                  RK,           name='registration_disallowed'),
      url(r'^activate/(?P<activation_key>\w+)/$', AV.as_view(), name='registration_activate'),
      url(r'^activated/$',               AC,           name='registration_activation_complete'),
    ),
  ),
  url_tree(r'', 'inkscape.person.views',
    url(r'^user/$',                   'my_profile',      name='my_profile'),
    url(r'^user/edit/$',              'edit_profile',    name='edit_profile'),
    url(r'^faces/$',                  'view_profiles',   name='faces'),
  ),
  USER_URLS,
)
