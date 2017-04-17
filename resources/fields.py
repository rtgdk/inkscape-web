"""
Allow tags to be created on the fly
"""

from collections import defaultdict

from django.forms import ValidationError
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from django.forms.models import ModelMultipleChoiceField
from django.forms.widgets import Select, SelectMultiple

from django.core.urlresolvers import reverse

from .validators import Range

class FilterSelect(Select):
    def __init__(self, qs, m2m_field, filter_by, replace):
        self.filter_by = filter_by
        self.filters = defaultdict(list)
        for (pk, m2m_pk) in list(qs.values_list('pk', m2m_field)):
            if m2m_pk is not None:
                self.filters[pk].append(int(m2m_pk))

        super(FilterSelect, self).__init__(replace.attrs, replace.choices)

    def render(self, name, value, attrs=None, choices=()):
        attrs = attrs or {}
        attrs['data-filter_by'] = self.filter_by
        return super(FilterSelect, self).render(name, value, attrs, choices)

    def render_option(self, selected_choices, value, label):
        label = force_text(label)
        value = force_text(value or '')
        html = ' selected="selected"' if value in selected_choices else ''
        if value and int(value) in self.filters:
            html += ' data-filter="%s"' % str(self.filters[int(value)])
        return '<option value="%s"%s>%s</option>' % (value, html, label)


class DisabledSelect(Select):
    """If there is only one choice, disable and set to this choice"""
    def render(self, name, value, attrs=None, choices=()):
        attrs = attrs or {}
        attrs['disabled'] = 'disabled'
        self.name = name
        return super(DisabledSelect, self).render(name+'_disabled', value, attrs, choices)[:-9]

    def render_option(self, selected_choices, value, label):
        label = force_text(label)
        if value:
            return '<option value="%s" selected="selected">%s</option></select>' % (value, label) + \
                   '<input type="hidden" name="%s" value="%s">' % (self.name, value)
        return ''

class CategorySelect(Select):
    """Provide extra data for validating a resource within the option"""
    def render_option(self, selected_choices, obj, label):
        label = force_text(label)
        value = force_text(obj or '')
        html = ''
        if obj and not isinstance(obj, (int, str, unicode)):
            # CSV list of types, treat as string
            if obj.acceptable_types:
                html += ' data-types="%s"' % obj.acceptable_types

            for field in ('media_x', 'media_y', 'size'):
                f_value = getattr(obj, 'acceptable_' + field)
                if f_value not in (None, ''):
                    scale = 1024 if field == 'size' else 1
                    for method in (min, max):
                        # Add both min and max for every range field
                        html += ' data-%s-%s="%d"' % (field,
                            method.__name__, method(Range(f_value)) / scale)
            value = force_text(obj.pk)

        html += ' selected="selected"' if value in selected_choices else ''
        return '<option value="%s"%s>%s</option>' % (value, html, label)

class SelectTags(SelectMultiple):
    SCRIPT = """
    <script>
      var existingTags = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
                    url: '/json/tags.json',
                    transform: function(response){
                                 return response.tags;
                                },
                    ttl: 60*1000 /* 1 minute */
        }
      });
       
      existingTags.initialize();

      $('#id_%(id)s').tagsinput({
        maxTags: 12,
        maxChars: 16,
        trimValue: true,
        typeaheadjs: {
          name: 'existingTags',
          display: 'name',
          source: existingTags.ttAdapter()
        }
      });
    </script>"""

    class Media:
        css = {
            'all': ('css/bootstrap-tagsinput.css', 'css/bootstrap-tagsinput-typeahead.css',)
        }
        js = ('js/bootstrap-tagsinput.js', 'js/typeahead.js')

    def render(self, name, value, **kwargs):
        html = super(SelectTags, self).render(name, value, **kwargs)
        url = reverse('ajax_lookup', kwargs={'channel': 'tags'})
        return mark_safe(html + (self.SCRIPT % {'id':name, 'ajax': url}))

    def render_option(self, selected_choices, option_value, label):
        """Only supply selected tags so tagsinput won't add them all"""
        # This isn't as efficient as it could be because it
        # still loops /every/ tag possible. Replace with selected_choices
        if force_text(option_value) in selected_choices:
            return super(SelectTags, self).render_option([], label, 'hidden')
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
                tag = tag.lower()
                yield Tag.objects.get_or_create(name=tag)[0].pk
            except Exception as error:
                if "value too long" in str(error):
                    raise ValidationError("Tag is too long!")
                raise

