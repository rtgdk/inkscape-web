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
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext_lazy as _
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect

from pile.views import DetailView
from .models import ContentType, MODERATED_INDEX

class ModerateMixin(object):
    def get_parent(self):
        return (reverse('moderation:index'), _("Moderation"))

    def get_model(self):
        ct = ContentType.objects.get_by_natural_key(self.kwargs['app'], self.kwargs['name'])
        return ct.model_class()

    def flag_class(self):
        return MODERATED_INDEX[self.kwargs['app'] + '.' + self.kwargs['name']]

class FunctionView(ModerateMixin, DetailView):
    """Access to moderator objects from urls makes things easier"""
    def get_object(self):
        return get_object_or_404(self.get_model(), pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        ret = self.function() if request.POST.get('confirm', False) else None
        if not ret:
            messages.error(request, self.confirm)
        elif isinstance(ret, tuple) and not ret[-1]:
            messages.warning(request, self.warning)
        else:
            messages.success(request, self.created)
        return redirect(self.next_url())

    def function(self):
        obj = self.get_object()
        return obj.moderation.flag(self.flag)

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

