# -*- coding: utf-8 -*-
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

from django.views.generic import ListView, DetailView

from .models import Platform, Release

class ReleaseList(ListView):
    template_name = 'releases/release_detail.html'
    model = Release

class ReleaseView(DetailView):
    model = Release
    slug_field = 'version'
    slug_url_kwarg = 'version'

    def get_object(self):
        if 'version' not in self.kwargs:
            return self.get_queryset().latest()
        return super(ReleaseView, self).get_object()

    def get_context_data(self, **kwargs):
        data = super(ReleaseView, self).get_context_data(**kwargs)
        tabs = list(data['object'].tabs)
        if tabs:
            data['platform'] = self.kwargs.get('platform', None)
        data['releases'] = Release.objects.all()
        return data

class PlatformList(ListView):
    queryset = Platform.objects.filter(parent__isnull=True)
    action = "Platform Managers"
    breadcrumbs = ('Platform Managers',)

