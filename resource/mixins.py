
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from pile.views import UpdateView, CreateView

from .models import Gallery, Model, Q

def next_url(request, default='/'):
    if isinstance(default, Model):
        default = default.get_absolute_url()
    return request.GET.get('next', request.META.get('HTTP_REFERER', default))

class OwnerUpdateMixin(object):
    def is_allowed(self):
        return self.get_object().user == self.request.user

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
        data['action'] = getattr(self, 'action', None)
        data['cancel'] = next_url(self.request)
        data['gallery'] = getattr(self, 'gallery', None)
        data['parent'] = data['gallery'] or self.request.user
        return data

class OwnerCreateMixin(OwnerUpdateMixin):
    def is_allowed(self):
        return self.request.user.is_authenticated()

