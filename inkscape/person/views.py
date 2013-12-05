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

@login_required
def my_profile(request):
    return view_profile(request, request.user.id)

def view_profile(request, user_id):
    c = {
        'user': get_object_or_404(User, id=user_id),
    }
    return render_to_response('person/profile.html', c,
        context_instance=RequestContext(request))

