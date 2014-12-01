
from django.template.base import Library
from django.conf import settings

from cms.models.pagemodel import Page

register = Library()

@register.filter("placeholder")
def add_placeholder(form, text=None):
    if text == None:
        raise ValueError("Placeholder requires text content for widget.")
    form.field.widget.attrs.update({ "placeholder": text })
    return form

@register.filter("tabindex")
def add_tabindex(form, number):
    form.field.widget.attrs.update({ "tabindex": number })
    return form

@register.filter("root_nudge")
def root_nudge(root, page):
    """
    django cms has a serious flaw with how it manages the 'root' of menus.
    This is because cms attempts to manage the root sent to menu via
    checking in_navigation options. this conflicts with the menus.NavigationNode
    system which controls the system via the templates.

    This tag stops django-cms interfering by correcting menus input when needed.
    """
    is_draft = page and page.publisher_is_draft or False
    for page in Page.objects.filter(is_home=True, publisher_is_draft=is_draft):
        return root + int(page.in_navigation)

