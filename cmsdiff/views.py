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
"""
Views for the cmsdiff functionality.
"""

from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, RedirectView
from django.template import RequestContext

from .models import Revision, RevisionDiff

class ViewDiff(DetailView):
    model = RevisionDiff
    template_name = "cmsdiff/revision_diff.html"

    def get_object(self):
        diff = super(ViewDiff, self).get_object()
        # Attempt to re-attach deleted revision
        if not diff.revision and diff.revisions.count() > 0:
            diff = diff.revisions.all()[0].diff
        return diff


