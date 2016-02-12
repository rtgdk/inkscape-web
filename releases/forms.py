
import sys

from django.forms import ModelForm
from ajax_select import make_ajax_field

from .models import Release, Platform

class QuerySetMixin(object):
    """Allow querysets in forms to be redefined easily"""
    noop = lambda self, qs: qs

    def __init__(self, *args, **kwargs):
        super(QuerySetMixin, self).__init__(*args, **kwargs)
        for key, field in self.fields.items():
            if hasattr(field, 'queryset'):
                fn = getattr(self, '%s_queryset' % key, self.noop)
                field.queryset = fn(field.queryset)


class ReleaseForm(QuerySetMixin, ModelForm):
    manager = make_ajax_field(Release, 'manager', 'user')
    reviewer = make_ajax_field(Release, 'reviewer', 'user')

    def parent_queryset(self, qs):
        qs = qs.filter(parent__isnull=True)
        if self.instance.pk:
            qs = qs.exclude(id=self.instance.pk)
        return qs


class PlatformForm(QuerySetMixin, ModelForm):
    manager = make_ajax_field(Platform, 'manager', 'user')

    class Meta:
        exclude = ('codename',)

    def parent_queryset(self, qs):
        if self.instance.pk is not None:
            non_parents = [p.pk for p in self.instance.descendants()]
            non_parents += [self.instance.pk]
            return qs.exclude(pk__in=non_parents)
        return qs

