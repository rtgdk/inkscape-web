# -*- coding: utf-8 -*-
#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#

from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

from registration.backends.default.views import ActivationView as AV, RegistrationView

from .views import *
from .forms import RegisForm, PasswordForm

def url_tree(regex, view='', *urls):
    return url(regex, include(patterns(view, *urls)))

AC = TemplateView.as_view(template_name='registration/activation_complete.html')
RC = TemplateView.as_view(template_name='registration/registration_complete.html')
RK = TemplateView.as_view(template_name='registration/registration_closed.html')
RG = RegistrationView.as_view(form_class=RegisForm)
UIDB = r'^(?P<uidb64>[0-9A-Za-z_\-]+?)/(?P<token>.+)/$'

# Our user url implementation allows other urls files to add
# their own urls to our user tree. Creating user functions.
USER_URLS = url_tree(r'^~(?P<username>[^\/]+)', 'person.views',
  url(r'^/?$',               UserDetail(),       name='view_profile'),
  url(r'^/gpg/$',            UserGPGKey(),       name='user_gpgkey'),
  url(r'^/friend/$',         MakeFriend(),       name='user_friend'),
  url(r'^/unfriend/$',       LeaveFriend(),      name='user_unfriend'),
)
TEAM_URLS = url_tree(r'^\*(?P<team>[^\/]+)', 'person.views',
  url(r'^/?$',               TeamDetail(),       name='team'),
  url(r'^/join/$',           AddMember(),        name='team.join'),
  url(r'^/leave/$',          RemoveMember(),     name='team.leave'),
  url(r'^/watch/$',          WatchTeam(),        name='team.watch'),
  url(r'^/unwatch/$',        UnwatchTeam(),      name='team.unwatch'),
  url(r'^/chat/$',           ChatWithTeam(),     name='team.chat'),
  url(r'^/charter/$',        TeamCharter(),      name='team.charter'),
  
  url_tree(r'^/(?P<username>[^\/]+)/', 'person.views',
    url(r'^remove/$',        RemoveMember(),      name='team.remove'),
    url(r'^approve/$',       AddMember(),         name='team.approve'),
    url(r'^disapprove/$',    AddMember(no=True),  name='team.disapprove'),
  ),
)

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
  url_tree(r'', 'person.views',
    url(r'^user/$',                   MyProfile.as_view(),   name='my_profile'),
    url(r'^user/edit/$',              EditProfile.as_view(), name='edit_profile'),
    url(r'^user/cla-agree/$',         AgreeToCla.as_view(),  name='agree_to_cla'),
    url(r'^user/welcome/$',           Welcome(),             name='welcome'),
    url(r'^teams/$',                  TeamList.as_view(),    name='teams'),
  ),
  USER_URLS,
  TEAM_URLS,
)
