# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.contrib.auth.models import User

from .models import UserDetails
from .forms import UserForm, UserDetailsForm

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


def view_profile(request, username):
    user = get_object_or_404(User, username=username)
    if request.user != user:
        user.details.visits += 1
        user.details.save()
    c = {
        'user'  : user,
        'items' : user.galleries.for_user(request.user),
        'me'    : user == request.user,
    }
    return render_to_response('person/profile.html', c,
        context_instance=RequestContext(request))

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

