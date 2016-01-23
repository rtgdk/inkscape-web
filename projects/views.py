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
from django.views.generic import ListView
from django.db.models import Q

from pile.views import DetailView, CategoryListView, CreateView, UpdateView, breadcrumbs
from .models import Project, ProjectUpdate

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


# Google Summer of Code Projects
class ProjectGsocList(ListView):
    template_name = 'projects/project_gsoc_list.html'
    model = Project
    cats = (
    ('project_type', 'type'),
    )
    opts = (
    ('complete', 'completed__isnull'),
    )
 
    def get_context_data(self, **kwargs):
        data = ListView.get_context_data(self, **kwargs)
        data['breadcrumbs'] = breadcrumbs(
        ('projects.gsoc', 'Google Summer of Code Projects'),
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

class NewProject(CreateView):
    model = Project
    fields = ('title', 'project_type', 'desc')

    def get_context_data(self, **kwargs):
        data = CreateView.get_context_data(self, **kwargs)
        data['breadcrumbs'] = breadcrumbs(
            ('projects', 'Projects'),
            'Propose Project',
        )
        return data

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.proposer = self.request.user
        obj.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('projects')
  
class UpdateProject(CreateView):
    model = ProjectUpdate
    fields = ('describe', 'image')
    
    def get_project(self):
      return Project.objects.get(slug=self.kwargs['project'])
    
    def get_context_data(self, **kwargs):
      data = super(CreateView, self).get_context_data(**kwargs)
      data['project'] = self.get_project()
      data['breadcrumbs'] = breadcrumbs(
            ('projects', 'Projects'),
            'Update Project',
        )
      return data

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.project = self.get_project()
        obj.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('project', kwargs={'slug': self.kwargs['project']})

class MyProjects(CategoryListView):
    model = Project
    
    def get_context_data(self, **kwargs):
        data = CategoryListView.get_context_data(self, **kwargs)
        data['breadcrumbs'] = breadcrumbs(
            (self.request.user, str(self.request.user.details)),
            'My Projects',
        )
        return data
    
    def get_queryset(self, **kwargs):
        # can't filter by method, only by db fields
        q = super(MyProjects, self).get_queryset(**kwargs).filter(
                    Q(workers__user=self.request.user) | 
                    Q(proposer=self.request.user) | 
                    Q(manager=self.request.user) | 
                    Q(reviewer=self.request.user) | 
                    Q(second=self.request.user)).distinct()
        return q