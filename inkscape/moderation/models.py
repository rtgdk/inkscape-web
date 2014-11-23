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

from .meta_manager import meta_manager_getter, isclass

# We're going to start with fixed flag types
FLAG_TYPES = (
    ('flag',    _('Removal Suggestion')),
    ('delete',  _('Moderator Deletion')),
    ('approve', _('Moderator Approval')),
)

from django.template import loader

class FlagManager(Manager):
    """Generated content based on Flag"""
    def categories(self):
        query = self.get_query_set()
        for content_type in query.values_list('content_type', flat=True).distinct():
            ct = ContentType.objects.get(pk=content_type)
            yield Flag.meta_manager(ct.model_class())

    def get_or_create(self, **kwargs):
        if 'content_object' in kwargs:
            obj = kwargs.pop('content_object')
            kwargs['object_pk'] = obj.pk
            kwargs['content_type'] = ContentType.objects.get_for_model(type(obj))
        return super(FlagManager, self).get_or_create(**kwargs)

    def flag_item(self, obj, user, flag='flag'):
        """Actually perform the flagging of a comment from a request."""
        flag, created = self.get_or_create(content_object=obj, flag=flag, user=user)
        return flag

    def latest(self):
        return self.get_query_set().order_by('-flaged')[:5]

    def template(self):
        try:
            template = 'moderation/items/%s.html' % str(self).lower()
            loader.get_template(template)
            return template
        except Exception:
            return None


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

    objects = FlagManager()

    class Meta:
        unique_together = [('user', 'object_pk', 'content_type', 'flag')]

    def __str__(self):
        return "%s of %s %s by %s" % (self.flag, self.content_type,
            self.object_pk, self.user.get_username())


get_my_flags = meta_manager_getter(Flag)


