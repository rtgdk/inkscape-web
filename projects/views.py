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

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from pile.views import DetailView, CategoryListView, breadcrumbs
from .models import Project

class ProjectList(CategoryListView):
    model = Project
    cats = (
      ('project_type', 'type'),
    )
    opts = (
      ('complete', 'completed__isnull'),
    )

    def get_context_data(self, **kwargs):
        data = CategoryListView.get_context_data(self, **kwargs)
        data['breadcrumbs'] = breadcrumbs(
            ('projects', 'Projects'),
        )
        return data


class ProjectView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        data = DetailView.get_context_data(self, **kwargs)
        data['breadcrumbs'] = breadcrumbs(
            ('projects', 'Projects'),
            data['object'],
        )
        return data

