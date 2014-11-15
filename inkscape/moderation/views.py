from django.shortcuts import render

from django.contrib.auth.decorators import login_required, permission_required

from django.db.models import Count
from django.views import generic
#from pile.views import *
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta

import django_comments


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
    
    #get all non-hidden, flagged, unapproved comments and reverse order them by number of flags
    def get_queryset(self):
      return django_comments.Comment.objects.all().filter(is_removed=0).exclude(flags__flag="moderator approval").annotate(flag_count=Count('flags')).filter(flag_count__gt=0).order_by("-flag_count")
    
class ModerateLatest(generic.ListView):
    template_name = 'comments/moderate_latest.html'
    context_object_name = 'comment_list'
    
    #prevent people who do not have comment moderation rights from accessing moderation page, shows 403 instead
    @method_decorator(permission_required("django_comments.can_moderate", raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(ModerateLatest, self).dispatch(*args, **kwargs)
    
    #get all comments from the last 30 days, including hidden ones
    def get_queryset(self):
      return django_comments.Comment.objects.all().filter(submit_date__gt=timezone.now() - timedelta(days=30)).order_by("-submit_date")
    
class HideComment(generic.DetailView):
    model = django_comments.Comment
    template_name = 'comments/hide_comment.html'
    
    #prevent people who do not have comment moderation rights from accessing moderation page, shows 403 instead
    @method_decorator(permission_required("django_comments.can_moderate", raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(HideComment, self).dispatch(*args, **kwargs)

#todo: don't count moderator approval flags in ModerateLatest query and pass the counted removal suggestion flags value to the template. 