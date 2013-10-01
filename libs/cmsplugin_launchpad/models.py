
import os
import datetime

from . import settings
from . import processors

from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


LEVELS = (
 ( '-', _('Unknown')  ),
 ( '?', _('Undecided')),
 ( 'C', _('Critical') ),
 ( 'H', _('High')     ),
 ( 'M', _('Medium')   ),
 ( 'L', _('Low')      ),
 ( 'W', _('Wishlist') ),
)

STATUS = (
 ( 'N', _('New')          ),
 ( 'I', _('Incomplete')   ),
 ( 'O', _('Opinion')      ),
 ( 'V', _('Invalid')      ),
 ( 'W', _('Won\'t Fix')   ),
 ( 'X', _('Expired')      ),
 ( 'F', _('Confirmed')    ),
 ( 'T', _('Triaged')      ),
 ( 'P', _('In Progress')  ),
 ( 'C', _('Fix Committed')),
 ( 'R', _('Fix Released') ),
 ( '-', _('Unknown')      ),
)

class Tag(models.Model):
    name    = models.CharField(_('Tag Name'),   max_length=32)

    def __unicode__(self):
        return self.name


class Bug(models.Model):
    bugid   = models.IntegerField(_('Bug Id'))
    created = models.DateTimeField(_('Date Created'))
    updated = models.DateTimeField(_('Date Updated'))

    title   = models.CharField(_('Title'),      max_length=255)
    level   = models.CharField(_('Importance'), max_length=1, choices=LEVELS)
    status  = models.CharField(_('Status'),     max_length=1, choices=STATUS)
    owner   = models.CharField(_('Owner'),      max_length=64)

    tags    = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.title


def BugList(models.Model):
    name = models.Charfield(_('List Name'), max_length=32)
    bugs = models.ManyToManyField(Bug)

    def refresh(self):
        """Fill the bug list with new information"""


class BugPlugin(CMSPlugin):
    source   = models.ForeignKey(BugList)
    limit    = models.PositiveIntegerField(_('Page Limit'))
    template = models.CharField(choices=settings.LP_TEMPLATES, max_length=255)


