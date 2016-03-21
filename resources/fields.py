"""
Allow tags to be created on the fly
"""

from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from django.forms.models import ModelMultipleChoiceField
from django.forms.widgets import SelectMultiple

from django.core.urlresolvers import reverse

SCRIPT = """
<script>
  $('#id_%(id)s').tagsinput({
    maxTags: 12,
    maxChars: 16,
    trimValue: true,
  });
</script>"""

class SelectTags(SelectMultiple):
    class Media:
        css = {
            'all': ('css/bootstrap-tagsinput.css',)
        }
        js = ('js/bootstrap-tagsinput.js',)

    def render(self, name, value, **kwargs):
        html = super(SelectTags, self).render(name, value, **kwargs)
        url  = reverse('ajax_lookup', kwargs={'channel': 'tags'})
        return mark_safe(html + (SCRIPT % {'id':name, 'ajax': url}))

    def render_option(self, selected_choices, option_value, option_label):
        """Only suply selecte tags so tagsinput won't add them all"""
        # XXX This isn't as efficient as it could be because it
        # still loops /every/ tag possible. Replace with selected_choices
        if force_text(option_value) in selected_choices:
            return super(SelectTags, self).render_option([], option_label, 'hidden')
        return ''


class TagsChoiceField(ModelMultipleChoiceField):
    widget = SelectTags

    def _check_values(self, value):
        tags = list(self.get_or_create(value))
        return super(TagsChoiceField, self)._check_values(tags)

    def get_or_create(self, values):
        from .models import Tag
        for tag in frozenset(values):
            if isinstance(tag, int) or tag.isdigit():
                yield tag
                continue
            try:
                tag = tag.replace('_', ' ').replace('-', ' ').title()
                yield Tag.objects.get_or_create(name=tag)[0].pk
            except Exception as error:
                if "value too long" in str(error):
                    raise ValidationError("Tag is too long!")
                raise


