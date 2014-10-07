# -*- coding: utf-8 -*-
#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from pile.views import CategoryListView

from .models import UserAlert

class AlertList(CategoryListView):
    model = UserAlert
    opts = (
      ('alert', 'slug'),
#      ('', ''),
    )
    def get_queryset(self, *args, **kwargs):
        query = CategoryListView.get_queryset(self, *args, **kwargs)
        return query.filter(viewed__isnull=True)

# XXX View to send a message to another user

@login_required
def mark_viewed(request, alert_id):
    alert = get_object_or_404(UserAlert, pk=alert_id, user=request.user)
    alert.view()
    return HttpResponse(alert.pk)


