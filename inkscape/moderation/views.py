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
from django.utils import timezone
from datetime import timedelta

from django.utils.translation import ugettext_lazy as _

from pile.views import *

from .models import *
from .mixins import *


class FlagObject(UserRequired, FunctionView):
    template_name = 'moderation/flag.html'
    confirm = _('Flagging Canceled')
    created = _('Moderators have been notified of the issue you have reported.')
    warning = _('You have already flagged this item for attention.')
    flag = 1


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
        return self.get_model().moderation.all()


class ModerateLatest(ModeratorRequired, CategoryListView):
    template_name = 'moderation/latest.html'
    
    def get_queryset(self):
        """get all comments from the last 30 days, including hidden ones"""
        return self.get_models().objects.all()


class HideComment(ModeratorRequired, FunctionView):
    template_name = 'moderation/flag.html'
    confirm = _('Hiding Canceled')
    created = _('Item has been hidden!')
    warning = _('Item was already hidden.')
    flag = 10

class ApproveComment(ModeratorRequired, FunctionView):
    template_name = 'moderation/flag.html'
    confirm = _('Approve Canceled')
    created = _('Item has been Approved.')
    warning = _('Item has already been approved.')
    flag = 5

