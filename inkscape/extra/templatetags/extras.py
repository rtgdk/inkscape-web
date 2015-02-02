
from django.utils.timezone import is_aware, utc

# Not the typical translator
from django.utils.translation import ungettext_lazy as _un, ugettext_lazy as _

from datetime import datetime
from django.template.base import Library
from django.conf import settings

from cms.models.pagemodel import Page

register = Library()


CHUNKS_AGO = (
  # Note to translator: Short varients are for display. Keep short but use your better judgement.
  (60 * 60 * 24 * 365, _un('%d year ago',   '%d years ago'),  _('%dyr')),
  (60 * 60 * 24 * 30,  _un('%d month ago',  '%d months ago'), _('%dmon')),
  (60 * 60 * 24 * 7,   _un('%d week ago',   '%d weeks ago'),  _('%dwk')),
  (60 * 60 * 24,       _un('%d day ago',    '%d days ago'),   _('%dd')),
  (60 * 60,            _un('%d hour ago',   '%d hours ago'),  _('%dhr')),
  (60,                 _un('%d minute ago', '%d minutes ago'),_('%dmin'))
)

@register.filter("ago")
def time_ago(d, mode=0):
    if not d: 
        return _('Never')
    # Convert datetime.date to datetime for comparison.
    if not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day)

    now = datetime.now(utc if is_aware(d) else None)

    delta = (now - d)
    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return _('Now') if int(mode) == 1 else _('0 minutes')
    for i, (seconds, name, small) in enumerate(CHUNKS_AGO):
        count = since // seconds
        if count != 0:
            break
    result = (int(mode) == 1 and small or name) % count
    if i + 1 < len(CHUNKS_AGO) and int(mode) == 0:
        # Now get the second item
        seconds2, name2, small2 = CHUNKS_AGO[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            result += ', ' + (name2 % count2)
    return result

@register.filter("percent")
def percent(x, y):
    return "%d%%" % ( float(x) / float(y) )

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

