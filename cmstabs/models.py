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
"""
Extra models for cms widgets only useful to inkscape website
"""

__all__ = ('TabCategory', 'Tab', 'ShieldPlugin', 'InlinePages', 'InlinePage', 'GroupPhotoPlugin', 'InkPicture')

import os
import sys

from django.conf import settings
from django.db.models import *
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from cms.models import CMSPlugin, Page

try:
    from cms.models import get_plugin_media_path
except ImportError:
    def get_plugin_media_path(instance, filename):
        """
        See cms.models.pluginmodel.get_plugin_media_path on django CMS 3.0.4+
        for information
        """
        return instance.get_media_path(filename)
from cms.utils.compat.dj import python_2_unicode_compatible

from pile.fields import ResizedImageField

from resources.models import License

null = dict(null=True, blank=True)

class TabCategory(Model):
    name   = CharField(max_length=22)
    icon   = ResizedImageField(_('Icon'), 32, 32, upload_to='shields/icons')

    class Meta:
        db_table = 'extra_tabcategory'

    def __unicode__(self):
        return self.name

BTNS = (
  ('download', _('Download Icon')),
)

class Tab(Model):
    link     = URLField(_('External Link'), **null)
    name     = CharField(max_length=64)
    user     = ForeignKey(settings.AUTH_USER_MODEL, related_name='front_tabs', **null)
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
        db_table = 'extra_tab'

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

    class Meta:
        db_table = 'extra_shieldplugin'

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


class InlinePages(CMSPlugin):
    class Meta:
        db_table = 'extra_inlinepages'

    def __unicode__(self):
        return u"%d Inline Pages" % self.cmsplugin_set.all().count()


class InlinePage(CMSPlugin):
    title = CharField(max_length=64)

    class Meta:
        db_table = 'extra_inlinepage'

    def __unicode__(self):
        return self.title


class GroupPhotoPlugin(CMSPlugin):
    STYLES = ( 
      ('L', _('Simple List')),
      ('P', _('Photo Heads')),
      ('B', _('Photo Bios')),
    )   

    source = ForeignKey(Group)
    style  = CharField(_('Display Style'), max_length=1, choices=STYLES)

    class Meta:
        db_table = 'person_groupphotoplugin'

@python_2_unicode_compatible
class InkPicture(CMSPlugin):
    """
    A Picture with or without a link, with or without captions, in raster or vector format.
    """
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    FLOAT_CHOICES = ((LEFT, _("left")),
                     (RIGHT, _("right")),
                     (CENTER, _("center")),
                     )

    # Relying on browser to decide if image or not
    image = FileField(_("Image File"), upload_to=get_plugin_media_path)

    url = CharField(
        _("Link"), max_length=255, blank=True, null=True,
        help_text=_("If present, clicking on image will take user to link."))

    page_link = ForeignKey(
        Page, verbose_name=_("CMS page link"), null=True,
        limit_choices_to={'publisher_is_draft': True}, blank=True,
        help_text=_("If present, clicking on image will take user to "
                    "specified cms page."))

    alt = CharField(
        _("Alternate text"), max_length=255, blank=True, null=True,
        help_text=_("Specifies an alternate text for an image, if the image"
                    "cannot be displayed.<br />Is also used by search engines"
                    "to classify the image."))

    title = CharField(
        _("Hover text"), max_length=255, blank=True, null=True,
        help_text=_("When user hovers above picture, this text will appear "
                    "in a popup."))
    caption = CharField(
        _("Image caption"), max_length=512, blank=True, null=True,
        help_text=_("If set, the image will be nested into a figure tag "
                    "together with this caption."))

    float = CharField(
        _("side"), max_length=10, blank=True, null=True, choices=FLOAT_CHOICES,
        help_text=_("Move image left, right or center."))

    width = IntegerField(_("width"), blank=True, null=True,
                                help_text=_("Width of the image in pixels. "
                                            "If set, image will be scaled proportionately.")) # maybe not in IE...
                                
    extra_styling = CharField(
        _("Extra styles"), max_length=255, blank=True, null=True,
        help_text=_("Additional styles to apply to the figure or img element, e.g. 'margin-top: 0.5em; border: 1px solid grey;'. Be careful to not break the layout!"))

    def __str__(self):
        if self.alt:
            return self.alt[:40]
        elif self.image:
            # added if, because it raised attribute error when file wasn't
            # defined.
            try:
                return u"%s" % os.path.basename(self.image.name)
            except AttributeError:
                pass
        return u"<empty>"

    def clean(self):
        if self.url and self.page_link:
            raise ValidationError(
                _("You can enter a Link or a Page, but not both."))
