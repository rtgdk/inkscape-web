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

from django.views.generic import TemplateView, RedirectView
from django.core.urlresolvers import reverse

from reversion.models import Revision
from .utils import RevisionDiff

class DiffRedirect(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kw):
        revision_to = Revision.objects.get(pk=self.kwargs['pk'])
        revision_from = revision_to.previous
        pk = revision_from.pk if revision_from else 0
        args = '?revision_from=%d&revision_to=%d' % (pk, revision_to.pk)
        return reverse('cms.diff') + args


class DiffView(TemplateView):
    template_name = "cmsdiff/revision_diff.html"

    def get_context_data(self, **kw):
        data = super(DiffView, self).get_context_data(**kw)
        ids = sorted([
          int(self.request.GET['revision_from']),
          int(self.request.GET['revision_to']),
        ])
        data['diff'] = RevisionDiff(*ids)
        return data


