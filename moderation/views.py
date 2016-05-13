#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#
from django.utils import timezone
from datetime import timedelta

from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, ListView

from .models import *
from .mixins import *

class FlagObject(UserRequired, FunctionView):
    title = _("Flag Object")
    template_name = 'moderation/flag.html'
    confirm = _('Flagging Canceled')
    created = _('Moderators have been notified of the issue you have reported.')
    warning = _('You have already flagged this item for attention.')
    flag = 1


class Moderation(ModeratorRequired, TemplateView):
    title = _("Moderators' Area")
    template_name = 'moderation/flag_list.html'

    def get_context_data(self, **data):
        data = super(Moderation, self).get_context_data(**data)
        data['categories'] = MODERATED_SELECTIONS
        return data


class ModerateFlagged(ModerateMixin, ModeratorRequired, ListView):
    title = _("Moderate Flagged Items")
    template_name = 'moderation/flag_flagged.html'
    
    def get_queryset(self):
        """get all non-hidden, flagged, unapproved comments and reverse
           order them by number of flags"""
        return self.flag_class().objects.all()


class ModerateLatest(ModerateMixin, ModeratorRequired, ListView):
    title = _("Moderate Latest Items")
    template_name = 'moderation/flag_latest.html'
    
    def get_queryset(self):
        """get all comments from the last 30 days, including hidden ones"""
        try:
            return self.get_model().objects.latest()[:30]
        except AssertionError:
            return self.get_model().objects.order_by('id')[:30]


class HideComment(ModeratorRequired, FunctionView):
    title = _("Hide Comment")
    template_name = 'moderation/flag.html'
    confirm = _('Hiding Canceled')
    created = _('Item has been hidden!')
    warning = _('Item was already hidden.')
    flag = 10


class ApproveComment(ModeratorRequired, FunctionView):
    title = _("Approve Comment")
    template_name = 'moderation/flag.html'
    confirm = _('Approve Canceled')
    created = _('Item has been Approved.')
    warning = _('Item has already been approved.')
    flag = 5

