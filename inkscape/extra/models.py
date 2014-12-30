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
Extra models for cms widgets only useful to inkscape website
"""

__all__ = ('TabCategory', 'Tab', 'ShieldPlugin')

import os
import sys

from django.db.models import *
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.utils.text import slugify
from django.core.urlresolvers import reverse

from cms.models import CMSPlugin
from pile.fields import ResizedImageField

from inkscape.resource.models import License, User

null = dict(null=True, blank=True)

class TabCategory(Model):
    name   = CharField(max_length=22)
    icon   = ResizedImageField(_('Icon'), 32, 32, upload_to='shields/icons')

    def __unicode__(self):
        return self.name

BTNS = (
  ('download', _('Download Icon')),
)

class Tab(Model):
    link     = URLField(_('External Link'), **null)
    name     = CharField(max_length=64)
    user     = ForeignKey(User, related_name='front_tabs', **null)
    download = FileField(_('Background'), upload_to='shields/backgrounds')
    license  = ForeignKey(License)

    order    = IntegerField(editable=True, **null)

    tab_name = CharField(_("Heading"), max_length=64)
    tab_text = CharField(_("Sub-Heading"), max_length=128)
    tab_cat  = ForeignKey(TabCategory, verbose_name=_("Tab Icon"))

    banner_text = CharField(max_length=255, **null)
    banner_foot = CharField(max_length=128, **null)

    btn_text = CharField(_("Button Text"), max_length=32, **null)
    btn_link = CharField(_("Button Link"), max_length=255, **null)
    btn_icon = CharField(_("Button Icon"), max_length=12, choices=BTNS, **null)

    # The backwards linking here is because django can't inline ManyToMany fields
    shield = ForeignKey('ShieldPlugin', related_name='tabs')
    draft  = ForeignKey('self', **null)

    class Meta:
        ordering = ('order',)

    @property
    def uuid(self):
        return slugify(self.tab_name)

    def __unicode__(self):
        return self.tab_name + (not self.draft and ' (draft)' or '')

    def save(self, **kwargs):
        if self.draft_id == self.pk:
            sys.stderr.write("Tab can't reference itself as a draft!\n")
            self.draft_id = None
        return super(Tab, self).save(**kwargs)
    
def fab(obj):
    return dict([ (f.name, getattr(obj, f.name)) for f in obj._meta.fields
             if not isinstance(f, AutoField) and '_ptr' not in f.name and\
                not f in obj._meta.parents.values()])

class ShieldPlugin(CMSPlugin):
    def get_translatable_content(self):
        """Build a dictionary of translatable fields"""
        tr_fields = {}
        for (i, obj) in enumerate(self.tabs.all()):
            for field in obj._meta.fields:
                if field and isinstance(field, (CharField, TextField))\
                   and not field.choices and field.editable and field.name\
                   and field.name not in ('btn_link', 'link'):
                    content = getattr(obj, field.name)
                    if content:
                        tr_fields['%s_%d' % (field.name, i)] = content
        return tr_fields

    def set_translatable_content(self, content):
        """Set the generated content back"""
        # XXX Take content and put into manytomany content here.
        self.save()
        return True

    def copy_relations(self, oldinstance):
        for tab in oldinstance.tabs.all():
            (obj, new) = Tab.objects.get_or_create(draft=tab, shield=self, defaults=fab(tab))
            obj.draft = tab
            obj.shield = self
            obj.save()


