# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.contrib.auth.models import User

from .models import UserDetails, Team
from .forms import UserForm, UserDetailsForm
from pile.views import *

@login_required
def edit_profile(request):
    user = request.user
    c = {
        'user': user,
        'user_form': UserForm(instance=user),
        'details_form': UserDetailsForm(instance=user.details),
    }
    if request.method == 'POST':
        form_a = UserForm(request.POST, instance=user)
        form_b = UserDetailsForm(request.POST, request.FILES,
                                 instance=user.details)

        if form_a.is_valid() and form_b.is_valid():
            form_a.save()
            form_b.save()
            return redirect('my_profile')
        c['user_form'] = form_a
        c['details_form'] = form_b

    return render_to_response('person/edit.html', c,
        context_instance=RequestContext(request))


from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_superuser)
def view_profiles(request):
    c = {
        'users': UserDetails.objects.all(),
    }
    return render_to_response('person/profiles.html', c,
        context_instance=RequestContext(request))


@login_required
def my_profile(request):
    return view_profile(request, request.user.username)


class UserDetail(DetailView):
    template_name  = 'person/user_detail.html'
    slug_url_kwarg = 'username'
    slug_field     = 'username'
    model = User

    def get_context_data(self, **kwargs):
        data = super(UserDetail, self).get_context_data(**kwargs)
        data['object'].visited_by(self.request.user)
        return data

class TeamDetail(DetailView):
    model = Team
    slug_url_kwarg = 'team_slug'

@login_required
def add_friend(request):
    # XXX to-do
    to_user = get_object_or_404(User, username=request.GET.get('u', '-1'))
    friendship = request.user.friends.create(friend=to_user)
    return HttpResponse(friendship.pk)

@login_required
def rem_friend(request, friend_id):
    friendship = get_object_or_404(Friend, pk=friend_id, user=request.user)
    friendship.delete()
    return HttpResponse(1)

def gpg_key(request, username):
    user = get_object_or_404(User, username=username)
    return render_to_response('person/gpgkey.txt', { 'user': user },
      context_instance=RequestContext(request),
      content_type="text/plain")


