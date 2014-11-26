#
# Copyright 2014, Maren Hachmann <maren@goos-habermann.de>
#                 Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from pile.views import *

from .models import *
from .mixins import *


class FlagObject(UserRequired, View):
    template_name = 'moderation/flag.html'

    def get(self, request, app, name, pk):
        ct = ContentType.objects.get_by_natural_key(app, name)
        obj = get_object_or_404(ct.model_class(), pk=pk)
        (flag, created) = obj.flag()
        if created:
            # <process form cleaned data>
            return redirect('success')
        return redirect('already-flagged')


class Moderation(ModeratorRequired, View):
    template_name = 'moderation/index.html'

    def get_context_data(self, **data):
        data = super(Moderation, self).get_context_data(**data)
        data['categories'] = MODERATED_CATEGORIES
        return data


class ModerateFlagged(ModeratorRequired, CategoryListView):
    template_name = 'moderation/flagged.html'
    
    def get_queryset(self):
        """get all non-hidden, flagged, unapproved comments and reverse
           order them by number of flags"""
        return Flag.objects.all()


class ModerateLatest(ModeratorRequired, CategoryListView):
    template_name = 'moderation/latest.html'
    
    def get_queryset(self):
        """get all comments from the last 30 days, including hidden ones"""
        return Flag.objects.all().filter(submit_date__gt=timezone.now() - timedelta(days=30)).order_by("-submit_date")
    
class HideComment(ModeratorRequired, DetailView):
    model = Flag
    template_name = 'comments/hide_comment.html'

class ApproveComment(ModeratorRequired, DetailView):
    model = Flag
    pass

#todo: don't count moderator approval flags in ModerateLatest query and pass the counted removal suggestion flags value to the template. 
