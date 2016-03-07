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
Logbook views based on request based entry point. Defaults to sitewide.
"""

from datetime import date

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView

from .models import LogMetric, LogRequest

class MetricList(ListView):
    model = LogMetric

class MetricDetails(DetailView):
    model = LogMetric
    slug_field = 'name'

class SiteWideStats(DetailView):
    action_name = _('Site Wide')
    model = LogRequest

    def get_object(self):
        return LogRequest.objects.get(path__isnull=True)

    def get_context_data(self, **kwargs):
        data = super(SiteWideStats, self).get_context_data(**kwargs)
        data['days'] = data['object'].days(today=date(2016, 01, 10))
        return data

class RequestStats(DetailView):
    model = LogRequest

    def get_object(self):
        path = self.kwargs['path'].replace('_', '/').strip('/')
        return LogRequest.objects.get(path=path)

