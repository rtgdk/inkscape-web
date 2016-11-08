#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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
    if int(y) == 0:
        return "0%"
    return '{:.0%}'.format(float(x) / float(y))

@register.filter("placeholder")
def add_placeholder(bound_field, text=None):
    if text == None:
        raise ValueError("Placeholder requires text content for widget.")
    bound_field.field.widget.attrs.update({ "placeholder": text })
    return bound_field

@register.filter("autofocus")
def add_autofocus(bound_field):
    bound_field.field.widget.attrs.update({ "autofocus": "autofocus" })
    return bound_field

@register.filter("tabindex")
def add_tabindex(bound_field, number):
    bound_field.field.widget.attrs.update({ "tabindex": number })
    return bound_field

@register.filter("formfield")
def add_form_control(bound_field):
    cls = ['form-control']
    if bound_field.errors:
        cls.append("form-control-danger")
    bound_field.field.widget.attrs.update({"class": ' '.join(cls)})
    return bound_field

@register.filter("is_checkbox")
def is_checkbox_field(bound_field):
    return type(bound_field.field.widget).__name__ == 'CheckboxInput'

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

