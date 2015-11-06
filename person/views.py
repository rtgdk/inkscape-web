# -*- coding: utf-8 -*-

#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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

from django.views.generic import UpdateView, DetailView, ListView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from user_sessions.views import LoginRequiredMixin

from .models import User, UserDetails, Group, Team
from .forms import PersonForm, AgreeToClaForm

class UserMixin(LoginRequiredMixin):
    def get_object(self):
        return self.request.user

class AgreeToCla(UserMixin, UpdateView):
    template_name = 'person/cla-agree.html'
    action_name = _('Contributors License Agreement')
    form_class = AgreeToClaForm

    def get_success_url(self):
        return self.request.POST.get('next', '/')

class EditProfile(UserMixin, UpdateView):
    form_class = PersonForm

    def get_success_url(self):
        return self.get_object().get_absolute_url()

class UserDetail(DetailView):
    template_name  = 'person/user_detail.html'
    slug_url_kwarg = 'username'
    slug_field     = 'username'
    model = User

    def get_object(self, **kwargs):
        user = super(UserDetail, self).get_object(**kwargs)
        user.visited_by(self.request.user)
        return user

class UserGPGKey(UserDetail):
    template_name = 'person/gpgkey.txt'
    content_type = "text/plain"

class MyProfile(UserMixin, UserDetail):
    pass

# ====== FRIENDSHIP VIEWS =========== #

class MakeFriend(LoginRequiredMixin, SingleObjectMixin, RedirectView):
    slug_url_kwarg = 'username'
    slug_field     = 'username'
    model          = User
    permanent      = False

    def get_object(self):
        user = SingleObjectMixin.get_object(self)
        (obj, new) = self.request.user.friends.get_or_create(user=user)
        if new:
            messages.success(self.request, "Friendship created with %s" % str(user))
        else:
            messages.error(self.request, "Already a friend with %s" % str(user))
        return user

    def get_redirect_url(self, **kwargs):
        return self.get_object().get_absolute_url()

class LeaveFriend(MakeFriend):
    def get_object(self):
        user = SingleObjectMixin.get_object(self)
        self.request.user.friends.filter(user=user).delete()
        messages.success(self.request, "Friendship removed from %s" % str(user))
        return user


# ====== TEAM VIEWS ====== #

class TeamList(ListView):
    queryset = Team.objects.exclude(enrole='S')

class TeamDetail(DetailView):
    slug_url_kwarg = 'team'
    model          = Team

class AddMember(LoginRequiredMixin, SingleObjectMixin, RedirectView):
    slug_url_kwarg = 'team'
    model          = Team
    permanent      = False

    def get_user(self):
        if 'username' in self.kwargs:
            return User.objects.get(username=self.kwargs['username'])
        return self.request.user

    def get_redirect_url(self, **kwargs):
        self.action(self.get_object(), self.get_user(), self.request.user)
        return self.get_object().get_absolute_url()

    def action(self, team, user, actor=None):
        if getattr(self, 'no', False):
            messages.warning(self.request, _("User Request Removed."))

        elif team.enrole == 'O' or \
          (actor == team.admin and team.enrole in 'PT') or \
          (actor in team.members.all() and team.enrole == 'P'):
            team.members.add(user)
            if self.mailing_list_modified(team, user):
                messages.info(self.request, _("Team membership added and user subscribed to mailing list."))
            else:
                messages.info(self.request, _("Team membership sucessfully added."))
        elif team.enrole in 'PT' and actor == user:
            team.requests.add(user)
            return messages.info(self.request, _("Membership Request Received."))
        else:
            return messages.error(self.request, _("Can't add user to team. (not allowed)"))
        team.requests.remove(user)

    def mailing_list_modified(self, team, user):
        return user in getattr(team, 'mailman_users', [])

class RemoveMember(AddMember):
    def action(self, team, user, actor=None):
        if actor in [user, team.admin]:
            team.members.remove(user)
            if self.mailing_list_modified(team, user):
                return messages.info(self.request, _("User removed from team and mailing list."))
            return messages.info(self.request, _("User removed from team."))
        messages.error(self.request, _("Cannot remove user from team. (not allowed)"))

class WatchTeam(AddMember):
    def action(self, team, user, actor=None):
        team.watchers.add(user)
        if self.mailing_list_modified(team, user):
            return messages.info(self.request, _("Now watching this team and subscribed to it's mailing list."))
        messages.info(self.request, _("Now watching this team"))

class UnwatchTeam(AddMember):
    def action(self, team, user, actor=None):
        team.watchers.remove(user)
        if self.mailing_list_modified(team, user):
            return messages.info(self.request, _("No longer watching this team or it's mailing list."))
        messages.info(self.request, _("No longer watching this team"))

