
from django.template.base import Library
from django.conf import settings

register = Library()

@register.filter("placeholder")
def add_placeholder(form, text=None):
    if text == None:
        raise ValueError("Placeholder requires text content for widget.")
    form.field.widget.attrs.update({ "placeholder": text })
    return form


