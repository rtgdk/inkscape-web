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

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from pile.views import UpdateView, CreateView

from .models import Gallery, Model, Q


class OwnerUpdateMixin(object):
    def is_allowed(self):
        obj = self.get_object()
        group = self.get_group()
        if group is not None and group in self.request.user.groups.all():
            return True
        return obj.user == self.request.user

    def get_group(self):
        return getattr(self.get_object(), 'group', None)

    def dispatch(self, request, *args, **kwargs):
        """ Making sure that only authors can update stories """
        if not self.is_allowed():
            raise PermissionDenied()
        try:
            self.gallery = Gallery.objects.get(
                Q(pk=kwargs['gallery_id']) & \
               (Q(user=request.user) | Q(group__in=request.user.groups.all())))
        except Gallery.DoesNotExist:
            raise PermissionDenied()
        except KeyError:
            pass
        return super(OwnerUpdateMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(OwnerUpdateMixin, self).get_context_data(**kwargs)
        data.update({
          'parent':  self.parent,
          'gallery': getattr(self, 'gallery', None),
          'action':  getattr(self, 'action', None),
          'cancel':  self.get_next_url(),
        })
        return data

    def get_next_url(self, default=None):
        if isinstance(default, Model):
            default = default.get_absolute_url()
        return self.request.GET.get('next', \
               self.request.META.get('HTTP_REFERER', default or '/'))

    @property
    def parent(self):
        return getattr(self, 'gallery', self.request.user)

    def get_success_url(self):
        try:
            return super(OwnerUpdateMixin, self).get_success_url()
        except:
            return self.get_next_url(self.parent)


class OwnerCreateMixin(OwnerUpdateMixin):
    def is_allowed(self):
        return self.request.user.is_authenticated()

