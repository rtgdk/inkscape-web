#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
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

from django.utils.text import slugify
from django.db.models import Q

def unique_slug(model, proposed, field='slug'):
    """Return a unique slug that doesn't exist already"""
    qs = Q(**{field: proposed}) | Q(**{field+'__startswith': proposed+'+'})
    existing = model.objects.filter(qs).values_list(field, flat=True)

    for increment in [u'%s+%d' % (proposed, x) for x in range(len(existing))]:
        if increment not in existing:
            return increment
    return proposed


def set_slug(obj, field='slug', source='name'):
    """Sets a slug attribute smartly"""

    original = (getattr(obj, field, '') or '').rsplit('+', 1)[0]
    proposed = slugify(unicode(getattr(obj, source)))

    if not original or proposed != original:
        setattr(obj, field, unique_slug(type(obj), proposed, field=field))

    return getattr(obj, field)
    

