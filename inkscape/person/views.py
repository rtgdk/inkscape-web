# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from django.contrib.auth.models import User

from .models import UserDetails
from .forms import UserForm, UserDetailsForm, FeedbackForm

from inkscape.settings import ADMINS
from django.core.mail import send_mail

def contact_us(request):
    form = FeedbackForm(request.POST or None)
    if form.is_valid():
        sender = 'Annonymous User <unknown@inkscape.org>'
        if request.user.is_authenticated():
            sender = request.user.email
            if request.user.first_name:
                sender = '%s %s <%s>' % (request.user.first_name, request.user.last_name, request.user.email)
        recipients = [ "%s <%s>" % (a,b) for (a,b) in ADMINS ]
        send_mail("Website Feedback", form.cleaned_data['comment'], sender, recipients)
        return render_to_response('feedback.html', {}, RequestContext(request))
    return render_to_response('feedback.html', { 'form': form }, RequestContext(request))


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
    return view_profile(request, request.user.id)


def view_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
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

