
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext

from django.db.models import Count
from django.views import generic
from django.utils.decorators import method_decorator

import django_comments

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

class Moderation(generic.ListView):
    template_name = 'comments/moderate.html'
    context_object_name = 'comment_list'
    
    @method_decorator(permission_required("django_comments.delete_comment"))
    def dispatch(self, *args, **kwargs):
        return super(Moderation, self).dispatch(*args, **kwargs)
    
    def get_queryset(self):
      return django_comments.Comment.objects.all().filter(is_removed=0).filter(flags__comment_id__gt=0).annotate(flag_count=Count('flags')).order_by("-flag_count")
    
#somehow show a 404 or a text saying 'would you like to help with commments moderation?" 
#instead of login page for logged in users who don't have permission and accidentally discover the moderation page