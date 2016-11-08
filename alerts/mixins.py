# -*- coding: utf-8 -*-
#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.conf import settings

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic.detail import SingleObjectMixin

class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)

class UserRequiredMixin(object):
    def is_authorised(self, user):
        return True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_URL)
        if not self.is_authorised(request.user):
            raise PermissionDenied()
        return super(UserRequiredMixin, self).dispatch(request, *args, **kwargs)

class UserMixin(UserRequiredMixin):
    get_object = lambda self: self.request.user

class OwnerRequiredMixin(UserRequiredMixin):
    user_field = 'user'

    def is_authorised(self, user):
        if isinstance(self, SingleObjectMixin):
            return getattr(self.get_object(), self.user_field) == user

        # For lists of items
        qs = self.get_queryset()
        kw = {self.user_field: user}
        return qs.exclude(**kw).count() == 0
        

