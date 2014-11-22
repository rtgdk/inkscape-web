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
This creates a method which can be used to get flags of any object via that object's
own use of the function. Shunting the related manager on top of the original just like
ForeignKey's related_name but with GenericforeignKey
"""
#
# WARNING! High magic field ahead. Do not read unless level 12 Rincewind class wizzard.
#
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from inspect import isclass

def meta_manager_getter(rel, rel_name='content_object'):
    class MetaManager(rel._default_manager.__class__):
        def __init__(self, instance):
            super(MetaManager, self).__init__()
            self.instance = instance
            if not self.model:
                self.model = rel

        def get_query_set(self):
            queryset = super(MetaManager, self).get_query_set()
            if self.instance:
                if isclass(self.instance):
                    i_cls = self.instance
                else:
                    i_cls = type(self.instance)

                ct = ContentType.objects.get_for_model(i_cls)
                field = getattr(rel, rel_name)

                queryset = queryset.filter(**{field.ct_field: ct})
                if not isclass(self.instance):
                    queryset = queryset.filter(**{field.fk_field: field.pk})
            return queryset

    rel.meta_manager = MetaManager
    def _outer():
        def _inner(self):
            return MetaManager(self)
        return property(_inner)
    return _outer

