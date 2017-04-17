#
# Copyright 2017, Martin Owens <doctormo@gmail.com>
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
Provide a tool for getting moderation urls.
"""

from django.core.urlresolvers import reverse
from django.template.base import Library
from django.conf import settings

from django.contrib.contenttypes.models import ContentType

from moderation.models import FlagObject, FlagVote

register = Library()

@register.simple_tag(takes_context=True)
def flag_url(context, obj=None):
    if obj is None:
        obj = context['object']
    ct = ContentType.objects.get_for_model(obj)
    return reverse("moderation:flag", kwargs={
        'app': ct.app_label,
        'name': ct.model,
        'pk': obj.pk,
    })

@register.filter
def is_flagged(obj, user):
    if user and user.is_authenticated():
        ct = ContentType.objects.get_for_model(obj)
        return FlagVote.objects.filter(
            moderator_id=user.pk,
            target__content_type_id=ct.id,
            target__object_id=obj.pk
        ).count() > 0
    return False

