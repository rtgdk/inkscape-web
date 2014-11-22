from django.shortcuts import render

from django.contrib.auth.decorators import login_required, permission_required

from django.db.models import Count
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta

from pile.views import *

from .models import *

class ModeratorRequiredMixin(object):
    """Prevent people who do not have comment moderation rights from
       accessing moderation page, shows 403 instead."""
    @method_decorator(permission_required("moderation.can_moderate", raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ModeratorRequiredMixin, self).dispatch(request, *args, **kwargs)


class Moderation(ModeratorRequiredMixin, View):
    template_name = 'moderation/index.html'


class ModerateFlagged(ModeratorRequiredMixin, CategoryListView):
    template_name = 'moderation/flagged.html'
    
    def get_queryset(self):
        """get all non-hidden, flagged, unapproved comments and reverse
           order them by number of flags"""
        return Flag.objects.all()
        #filter(is_removed=0).exclude(flags__flag="moderator approval")
        #.annotate(flag_count=Count('flags')).filter(flag_count__gt=0).order_by("-flag_count")


class ModerateLatest(ModeratorRequiredMixin, CategoryListView):
    template_name = 'moderation/latest.html'
    
    def get_queryset(self):
        """get all comments from the last 30 days, including hidden ones"""
        return Flag.objects.all().filter(submit_date__gt=timezone.now() - timedelta(days=30)).order_by("-submit_date")
    
class HideComment(ModeratorRequiredMixin, DetailView):
    model = Flag
    template_name = 'comments/hide_comment.html'
    
#todo: don't count moderator approval flags in ModerateLatest query and pass the counted removal suggestion flags value to the template. 
