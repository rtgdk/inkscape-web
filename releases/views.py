# -*- coding: utf-8 -*-
#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from pile.views import DetailView, ListView, breadcrumbs
from .models import Release

class ReleaseList(ListView):
    model = Release

    def get_context_data(self, **kwargs):
        data = ListView.get_context_data(self, **kwargs)
        data['breadcrumbs'] = breadcrumbs(
            ('releases', _('Releases')),
        )
        return data

class ReleaseView(DetailView):
    model = Release
    slug_field = 'version'
    slug_url_kwarg = 'version'

    def get_object(self):
        if 'version' not in self.kwargs:
            qs = self.get_queryset()
            self.kwargs['version'] = qs[0].version if qs.count() else 'none'
        context = super(ReleaseView, self).get_object()
        setattr(context, 'releases', Release.objects.all())
        return context
