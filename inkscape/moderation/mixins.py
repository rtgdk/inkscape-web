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
"""
Basic mixin classes for moderators
"""

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

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

