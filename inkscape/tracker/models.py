from django.db import models

from django.utils.translation import ugettext_lazy as _

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


PRIORS = (
  ( '-', 'None' ),
  ( '?', 'Undefined' ),
  ( 'L', 'Low' ),
  ( 'M', 'Medium' ),
  ( 'H', 'High' ),
  ( 'E', 'Essential' ),
)

BLUEST = (
  ( 'A', 'Approved' ),
  ( 'P', 'Pending Approval' ),
  ( 'R', 'Review' ),
  ( 'D', 'Drafting' ),
  ( 'B', 'Discussion' ),
  ( 'N', 'New' ),
  ( 'S', 'Superseded' ),
  ( 'O', 'Obsolete' ),
)

CODEST = (
  ( '?', 'Unknown' ),
  ( '-', 'Not started' ),
  ( '/', 'Deferred' ),
  ( 'N', 'Needs Infrastructure' ),
  ( 'B', 'Blocked' ),
  ( 'S', 'Started' ),
  ( '<', 'Slow progress' ),
  ( '>', 'Good progress' ),
  ( 'A', 'Beta Available' ),
  ( 'R', 'Needs Code Review' ),
  ( 'D', 'Deployment' ),
  ( 'M', 'Implemented' ),
  ( 'I', 'Informational' ),
)


class Blueprint(models.Model):
    title    = models.CharField(_('Title'),    max_length=255)
    priority = models.TextField(_('Priority'), max_length=1, choices=PRIORS)
    delivery = models.TextField(_('Delivery'), max_length=1, choices=CODEST)
    approval = models.TextField(_('Approval'), max_length=1, choices=BLUEST)

    design   = models.BooleanField(_('Design Approved'))
    deliverd = models.BooleanField(_('Delivered'))

    desc     = models.TextField(_('Description'))


