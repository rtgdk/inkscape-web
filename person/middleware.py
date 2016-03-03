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
Model for specific user middleware
"""

from django.utils.timezone import now

class SetLastVisitMiddleware(object):
    """
    Provide a user tracking date/time stamp update middleware.
    """
    def process_request(self, request):
        """Process request happens before page view"""
        if request.user.is_authenticated():
            request.user.last_seen = now()
            request.user.save(update_fields=['last_seen'])

