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
"""
Person app mixins
"""

from user_sessions.views import LoginRequiredMixin

class UserMixin(LoginRequiredMixin):
    def get_object(self):
        return self.request.user

class NextUrlMixin(object):
    def get_success_url(self):
        if 'next' in self.request.POST:
            return self.request.POST['next']
        return self.get_object().get_absolute_url()
