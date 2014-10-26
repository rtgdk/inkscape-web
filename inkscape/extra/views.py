
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from .forms import FeedbackForm

from inkscape.settings import ADMINS
from django.core.mail import send_mail

def contact_us(request):
    form = FeedbackForm(request.POST or None)
    if form.is_valid():
        sender = 'Anonymous User <unknown@inkscape.org>'
        if request.user.is_authenticated():
            sender = request.user.email
            if request.user.first_name:
                sender = '%s %s <%s>' % (request.user.first_name, request.user.last_name, request.user.email)
        recipients = [ "%s <%s>" % (a,b) for (a,b) in ADMINS ]
        send_mail("Website Feedback", form.cleaned_data['comment'], sender, recipients)
        return render_to_response('feedback.html', {}, RequestContext(request))
    return render_to_response('feedback.html', { 'form': form }, RequestContext(request))


