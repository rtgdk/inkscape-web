
from django.db.models import CharField, ForeignKey
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin

class GroupPhotoPlugin(CMSPlugin):
    source = ForeignKey(Group)
    style  = CharField(_('Display Style'), max_length=1,
                       choices=(
                           ('L', _('Simple List')),
                           ('P', _('Photo Heads')),
                           ('B', _('Photo Bios')),
                       ))



