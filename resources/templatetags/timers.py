#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
"""
Provide useful tools for showing svg file in the templates directly.
"""

from datetime import datetime, timedelta

from django.template.base import Library
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_datetime, parse_date, parse_time

register = Library()

def _datetime(dt):
    """Forces a variable to be a datetime (not date or time)"""
    now = datetime.now(timezone.utc)
    if isinstance(dt, (str, unicode)):
        if ' ' in dt or 'T' in dt:
            dt = parse_datetime(dt)
        elif '-' in dt:
            dt = parse_date(dt)
        elif ':' in dt:
            dt = parse_time(dt)
        else:
            raise ValueError("Should be a datetime object, got string: %s" % dt)
    if not isinstance(dt, datetime) or not dt.tzinfo:
        return datetime(
            getattr(dt, 'year', now.year),
            getattr(dt, 'month', now.month),
            getattr(dt, 'day', now.day),
            getattr(dt, 'hour', 0),
            getattr(dt, 'minute', 0),
            getattr(dt, 'second', 0),
            getattr(dt, 'microsecond', 0),
            timezone.utc)
    return dt or now


@register.filter("timedelta")
def timedelta(dt, other=None):
    """Returns the clean timedelta for this dt, other can be any date/time or None for now()"""
    return _datetime(other) - _datetime(dt)

@register.filter("totalseconds")
def totalseconds(dt, other=None):
    """Return the number of seconds in this delta, can be positive or negative"""
    return timedelta(dt, other).total_seconds()

