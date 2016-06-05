
import sys

from django.forms import ModelForm, BaseInlineFormSet, inlineformset_factory
from ajax_select import make_ajax_field

# This dependance is fairly harsh, replace is possible.
from djangocms_text_ckeditor.widgets import TextEditorWidget

from .models import Release, Platform, ReleaseTranslation

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
    bug_manager = make_ajax_field(Release, 'bug_manager', 'user')
    translation_manager = make_ajax_field(Release, 'translation_manager', 'user')

    def __init__(self, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)
        if 'release_notes' in self.fields:
            self.fields['release_notes'].widget = TextEditorWidget()

    def parent_queryset(self, qs):
        qs = qs.filter(parent__isnull=True)
        if self.instance.pk:
            qs = qs.exclude(id=self.instance.pk)
        return qs


class ReleasePlatformForm(ModelForm):
    class Meta:
        exclude = ()

    def __init__(self, *args, **kwargs):
        super(ReleasePlatformForm, self).__init__(*args, **kwargs)
        if 'info' in self.fields:
            self.fields['info'].widget = TextEditorWidget()


class TranslationForm(ModelForm):
    class Meta:
        fields = ('language', 'translated_notes')

    def __init__(self, *args, **kwargs):
        super(TranslationForm, self).__init__(*args, **kwargs)
        if 'translated_notes' in self.fields:
            self.fields['translated_notes'].widget = TextEditorWidget()

TranslationInlineFormSet = inlineformset_factory(
    Release, ReleaseTranslation, form=TranslationForm, extra=1,
)

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

