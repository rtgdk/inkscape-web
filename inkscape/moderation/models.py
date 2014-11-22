#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Moderation is achieved using a generic flagging model and some further
 User monitoring which should allow users to manage each other in a
 healthy community atmosphere.

"""

from django.db.models import *
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.text import slugify

# We're going to start with fixed flag types
FLAG_TYPES = (
    ('flag',    _('Removal Suggestion')),
    ('delete',  _('Moderator Deletion')),
    ('approve', _('Moderator Approval')),
)

@python_2_unicode_compatible
class Flag(Model):
    """
    Records a flag on any object. A flag could be:

        * A "removal suggestion" -- where a user suggests a comment for (potential) removal.
        * A "moderator deletion" -- used when a moderator deletes a comment.

    You can (ab)use this model to add other flags, if needed. However, by
    design users are only allowed to flag a comment with a given flag once;
    if you want rating look elsewhere.
    """
    user    = ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Flagging User'), related_name="flaged_objects")
    flag    = CharField(_('Flag Type'), max_length=16, choices=FLAG_TYPES, db_index=True)
    flaged  = DateTimeField(_('Date Flagged'), default=now)

    # We can tag/flag any object with this meta-object key
    content_type   = ForeignKey(ContentType, related_name="content_type_set_for_%(class)s")
    object_pk      = TextField(_('object ID'))
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    class Meta:
        unique_together = [('user', 'object_pk', 'content_type', 'flag')]

    def __str__(self):
        return "%s flag of %s %s by %s" % (self.flag, self.content_type,
            self.comment_id, self.user.get_username())

#
# WARNING! High magic field ahead. Do not read unless level 12 Rincewind class wizzard.
#
# This creates a method which can be used to get flags of any object via that object's
# own use of the function. Shunting the related manager on top of the original just like
# ForeignKey's related_name but with GenericforeignKey
#

def meta_manager_getter(rel, rel_name='content_object'):
    class MetaManager(rel._default_manager.__class__):
        def __init__(self, instance):
            super(MetaManager, self).__init__()
            self.instance = instance

        def get_query_set(self):
            queryset = super(MetaManager, self).get_query_set()
            if self.instance:
                field = getattr(self.instance, rel_name)
                ct = rel.__class__.target.get_content_type(obj=self.instance)
                queryset = queryset.filter(**{
                    '%s' % field.ct_field: ct,
                    '%s' % field.fk_field: field.pk
                })
            return queryset

    def _outer():
        def _inner(self):
            return MetaManager(self)
        return property(_inner)
    return _outer

get_my_flags = meta_manager_getter(Flag)


