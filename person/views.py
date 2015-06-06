# -*- coding: utf-8 -*-

from django.views.generic import UpdateView, DetailView, ListView, RedirectView
from django.views.generic.detail import SingleObjectMixin
from user_sessions.views import LoginRequiredMixin
from django.contrib import messages

from .models import User, UserDetails, Group, Team
from .forms import PersonForm

class UserMixin(LoginRequiredMixin):
    def get_object(self):
        return self.request.user

class EditProfile(UserMixin, UpdateView):
    form_class = PersonForm

    def get_success_url(self):
        return self.get_object().get_absolute_url()

class FacesView(LoginRequiredMixin, ListView):
    template_name = 'person/profiles.html'
    queryset = UserDetails.objects.all()

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

class TeamDetail(DetailView):
    slug_url_kwarg = 'team_slug'
    model = Team



