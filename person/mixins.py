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
# pylint: disable=too-few-public-methods,missing-docstring
"""
Person app mixins
"""

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kw):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kw)

class UserMixin(LoginRequiredMixin):
    """
    Returns the logged in user as the get_object focus
    """
    def get_object(self):
        return self.request.user

class NeverCacheMixin(object):
    """
    Never cache this page.
    """
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)

class NextUrlMixin(object):
    """
    Go to to 'next' attribute url once complete (get_success_url)
    """
    def get_success_url(self):
        if 'next' in self.request.POST:
            return self.request.POST['next']
        return self.get_object().get_absolute_url()
