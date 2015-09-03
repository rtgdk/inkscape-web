#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from reversion.revisions import revision_context_manager as manager
from cmsdiff.app import DRAFT_ID

class CommentMiddleware(object):
    """Adds a comment to the current draft revision if possible."""
    def process_request(self, request):
        self.comment = request.POST.get('revision_comment', None)
        if request.method == 'POST' and self.comment:
            manager.start()

    def process_response(self, request, response):
        if self.comment:
            manager.set_comment(DRAFT_ID + request.POST['revision_comment'])
            manager.end()
        return response

