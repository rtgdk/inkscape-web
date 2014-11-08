
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.template import RequestContext

from django.db.models import Count
from django.views import generic
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta

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

class Moderation(generic.TemplateView):
    template_name = 'comments/moderation.html'
  
    #prevent people who do not have comment moderation rights from accessing moderation page, shows 403 instead
    @method_decorator(permission_required("django_comments.can_moderate", raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(Moderation, self).dispatch(*args, **kwargs)

class ModerateFlagged(generic.ListView):
    template_name = 'comments/moderate_flagged.html'
    context_object_name = 'comment_list'
    
    #prevent people who do not have comment moderation rights from accessing moderation page, shows 403 instead
    @method_decorator(permission_required("django_comments.can_moderate", raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ModerateFlagged, self).dispatch(*args, **kwargs)
    
    #get all non-hidden, flagged comments and reverse order them by number of flags
    def get_queryset(self):
      return django_comments.Comment.objects.all().filter(is_removed=0).annotate(flag_count=Count('flags')).filter(flag_count__gt=0).order_by("-flag_count")
    
class ModerateLatest(generic.ListView):
    template_name = 'comments/moderate_latest.html'
    context_object_name = 'comment_list'
    
    #prevent people who do not have comment moderation rights from accessing moderation page, shows 403 instead
    @method_decorator(permission_required("django_comments.can_moderate", raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ModerateLatest, self).dispatch(*args, **kwargs)
    
    #get all non-hidden comments from the last 30 days
    def get_queryset(self):
      return django_comments.Comment.objects.all().filter(is_removed=0).filter(submit_date__gt=timezone.now() - timedelta(days=30)).order_by("-submit_date")
    
class ModerateComment(generic.DetailView):
    model = django_comments.Comment
    template_name = 'comments/moderate_comment.html'
    
    #prevent people who do not have comment moderation rights from accessing moderation page, shows 403 instead
    @method_decorator(permission_required("django_comments.can_moderate", raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ModerateComment, self).dispatch(*args, **kwargs)
    