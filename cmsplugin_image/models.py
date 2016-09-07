# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django.core.exceptions import ValidationError
from django.db.models import *
from django.utils.translation import ugettext_lazy as _

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

@python_2_unicode_compatible
class Image(CMSPlugin):
    """
    A Picture with or without a link, with or without captions, in raster or vector format.

    Replaces CMS-Plugin picture and migrates the table name (see migrations 0003).
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
    height = IntegerField(_("height"), blank=True, null=True,
                                 help_text=_("Height of the image in pixels. If set together with width, image may be scaled disproportionately."))                               
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
