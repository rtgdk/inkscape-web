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
"""
Basic mixin classes for moderators
"""

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView

from .models import FlagVote

class FunctionView(DetailView):
    """Access to moderator objects from urls makes things easier"""
    template_name = 'moderation/flag.html'

    def get_object(self):
        return get_object_or_404(self.get_model(), pk=self.kwargs['pk'])

    def get_model(self):
        keys = self.kwargs['app'], self.kwargs['name']
        return ContentType.objects.get_by_natural_key(*keys).model_class()

    def post(self, request, *args, **kwargs):
        confirm = request.POST.get('confirm', False)
        if not confirm:
            messages.error(request, self.confirm)
        else:
            typ, msg = self.function()
            getattr(messages, typ)(request, getattr(self, msg))
        return redirect(self.next_url())

    def flag(self, weight=1):
        return FlagVote.objects.flag(self.request.user, self.get_object(),
                 notes=self.request.POST.get('notes', None), weight=weight)

    def next_url(self, **data):
        return self.request.POST.get('next', self.request.META.get('HTTP_REFERER', '/')) or '/'

    def get_context_data(self, **data):
        data = super(FunctionView, self).get_context_data(**data)
        data['flag_type'] = self.flag
        return data


class ModeratorRequired(object):
    """Prevent people who do not have comment moderation rights from
       accessing moderation page, shows 403 instead."""
    @method_decorator(permission_required("moderation.can_moderate", raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(ModeratorRequired, self).dispatch(request, *args, **kwargs)

class UserRequired(object):
    """Only allow a logged in user for flagging"""
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserRequired, self).dispatch(request, *args, **kwargs)

