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

from django.conf import settings

from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from .models import Gallery, Model, Group, Q

class NotAllowed(KeyError):
    def __init__(self, msg):
        self.msg = msg

class OwnerViewMixin(object):
    """Doesn't limit the view, but provides user or group access and filtering"""
    @property
    def user(self):
        return self.kwargs.get('username', None)

    @property
    def team(self):
        return self.kwargs.get('team', None)

    def get_context_data(self, **kwargs):
        data = super(OwnerViewMixin, self).get_context_data(**kwargs)
        if self.user:
            data['user'] = get_user_model().objects.get(username=self.user)
            data['object_list'].instance = data['user']
        elif hasattr(self, 'team') and self.team:
            data['group'] = Group.objects.get(team__slug=self.team)
            data['object_list'].instance = data['group']
        return data

    def get_queryset(self):
        qs = super(OwnerViewMixin, self).get_queryset()
        if self.user:
            qs = qs.filter(user__username=self.user, group__isnull=True)
        elif self.team:
            qs = qs.filter(group__team__slug=self.team)
        return qs


class OwnerUpdateMixin(object):
    """Limit the get and post methods to the user or group owners"""
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
            if not request.user.is_authenticated() and request.method == 'GET':
                return redirect_to_login(request.build_absolute_uri())
            raise PermissionDenied()
        try:
            self.gallery = Gallery.objects.get(
                Q(pk=kwargs['gallery_id']) & \
               ( Q(user=request.user)
                 | Q(group__in=request.user.groups.all())
                 | (Q(category__isnull=False) & ~Q(category=0))
               ))
        except Gallery.DoesNotExist:
            raise PermissionDenied()
        except KeyError:
            pass
        return super(OwnerUpdateMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(OwnerUpdateMixin, self).get_context_data(**kwargs)
        data.update({
          'gallery': getattr(self, 'gallery', None),
          'cancel':  self.get_next_url(),
        })
        return data

    def get_next_url(self, default=None):
        if isinstance(default, Model):
            default = default.get_absolute_url()
        return self.request.GET.get('next', \
               self.request.META.get('HTTP_REFERER', default or '/'))

    def get_success_url(self):
        try:
            return super(OwnerUpdateMixin, self).get_success_url()
        except:
            return self.get_next_url(self.parent)


class OwnerCreateMixin(OwnerUpdateMixin):
    def is_allowed(self):
        return self.request.user.is_authenticated()

    def get_context_data(self, **kwargs):
        data = super(OwnerCreateMixin, self).get_context_data(**kwargs)
        if hasattr(self, 'model') and not 'object_list' in data:
	    data['object_list'] = self.model.objects.all()
	    data['object_list'].instance = self.request.user
        if 'gallery' in data and 'object' not in data:
            data['object'] = data['gallery']
        return data


class OwnerDeleteMixin(OwnerUpdateMixin):
    def get_success_url(self):
        # Called before object is deleted or edited
        obj = self.get_object().parent
        return getattr(obj, 'get_absolute_url', self.backup_url)()

    def backup_url(self):
        return reverse('my_profile')
