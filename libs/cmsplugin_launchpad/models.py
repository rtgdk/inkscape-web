
import os
from datetime import datetime, timedelta

from . import settings
from . import processors

from django.db.models import Model, CharField, ForeignKey, ManyToManyField, \
                             IntegerField, DateTimeField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from tzinfo import utc

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

class Project(Model):
    name   = CharField(_('Project Name'), max_length=32)
    lpname = CharField(_('Launchpad ID'), max_length=64)

    def __unicode__(self):
        return self.name


#class Tag(Model):
#    name    = CharField(_('Tag Name'),   max_length=32)
#
#    def __unicode__(self):
#        return self.name


#class Bug(Model):
#    """A cached bug report from launchpad"""
#    bugid   = IntegerField(_('Bug Id'), primary_key=True, unique=True)
#    created = DateTimeField(_('Date Created'))
#    updated = DateTimeField(_('Date Updated'))
#
#    title   = CharField(_('Title'),      max_length=255)
#    level   = CharField(_('Importance'), max_length=1, choices=LEVELS)
#    status  = CharField(_('Status'),     max_length=1, choices=STATUS)
#    owner   = CharField(_('Owner'),      max_length=64)
#
#    tags    = ManyToManyField(Tag)
#
#    first_sync = DateTimeField(_('First Synced'), auto_now_add=True)
#    last_sync  = DateTimeField(_('Last Synced'), auto_now=True)
#
#    def __unicode__(self):
#        return self.title

class BugCount(Model):
    """A query which can be run on the launchpad api to get a list of bugs"""
    name    = CharField(_('List Name'), max_length=32)
    project = ForeignKey(Project)
    bugs    = IntegerField(default=-1)
    updated = DateTimeField(auto_now=True)

    # Search field entries (should be automatically used)
    created_before  = DateTimeField(blank=True, null=True, help_text=_("That were created before the given date."))
    created_since   = DateTimeField(blank=True, null=True, help_text=_("That have been created since the given date."))
    modified_since  = DateTimeField(blank=True, null=True, help_text=_("That have been modified since the given date."))

    tags = CharField(max_length=255, null=True, blank=True,
             help_text=_("Tags to search. To exclude use '-tag' instead."))
    milestone = CharField(max_length=255, null=True, blank=True,
             help_text=_("Show only bug tasks targeted to this milestone."))
    #https://bugs.launchpad.net/inkscape/+bugs?field.searchtext=&orderby=-importance&field.status%3Alist=NEW&field.status%3Alist=CONFIRMED&field.status%3Alist=TRIAGED&field.status%3Alist=INPROGRESS&field.status%3Alist=FIXCOMMITTED&field.status%3Alist=INCOMPLETE_WITH_RESPONSE&field.status%3Alist=INCOMPLETE_WITHOUT_RESPONSE&assignee_option=any&field.assignee=&field.bug_reporter=&field.bug_commenter=&field.subscriber=&field.structural_subscriber=&field.milestone%3Alist=21423&field.tag=&field.tags_combinator=ANY&field.has_cve.used=&field.omit_dupes.used=&field.omit_dupes=on&field.affects_me.used=&field.has_patch.used=&field.has_branches.used=&field.has_branches=on&field.has_no_branches.used=&field.has_no_branches=on&field.has_blueprints.used=&field.has_blueprints=on&field.has_no_blueprints.used=&field.has_no_blueprints=on&search=Search

    # Possible fields for the future:
    affected_user = "Link to a person."
    assignee = "Link to a person."
    bug_commenter = "Link to a person."
    bug_reporter = "Link to a person."
    bug_subscriber = "Link to a person."
    bug_supervisor = "Link to a person."
    component = "Distribution package archive grouping. E.g. main, universe, multiverse."

    has_cve = "Show only bugs associated with a CVE"
    has_no_package = "Exclude bugs with packages specified"
    has_patch = "Show only bugs with patches available."
    importance = "Show only bugs with the given importance or list of importances."
    information_type = "Show only bugs with the given information type or list of information types."
    linked_branches = "Search for bugs that are linked to branches or for bugs that are not linked to branches."
    nominated_for = "Link to a distro_series."
    omit_duplicates = "Omit bugs marked as duplicate"
    omit_targeted = "Omit bugs targeted to a series"
    owner = "Link to a person."
    search_text = "Bug ID or search text."
    status = "Show only bugs with the given status value or list of values."
    status_upstream = "Indicates the status of any remote watches associated with the bug. Possible values include: pending_bugwatch, hide_upstream, resolved_upstream, and open_upstream."
    structural_subscriber = "Link to a person."
    tags_combinator = "ANY|ALL Search for any or all of the tags specified."

    ignore = ['id', 'name', 'bugs', 'project', 'updated']
    tr = { 'tags': 'tag' }

    def __unicode__(self):
        return self.name

    def count(self):
        """Returns the count, may cause a blocking launchpad request"""
        import sys
        threshold = datetime.now().replace(tzinfo=utc) - timedelta(hours=2)
        sys.stderr.write("Got %s for %s" % (self.name, threshold))
        if self.bugs == -1 or not self.updated or self.updated < threshold:
            sys.stderr.write("REFRESHING")
            self.refresh()
        sys.stderr.write("\n")
        return self.bugs

    @property
    def query(self):
        """Returns a launchpad query based on available fields"""
        result = {}
        for name in self._meta.get_all_field_names():
            if name not in self.ignore and hasattr(self, name):
                field = getattr(self, name)
                if field and unicode(field):
                    result[name] = unicode(field)
        return result

    @property
    def field_query(self):
        for (name, value) in self.query.iteritems():
            yield "field.%s=%s" % (self.tr.get(name, name), value)

    def link(self):
        """Tries to return a generated link"""
        return "https://bugs.launchpad.net/%s/+bugs?orderby=-importance&%s" % (
            self.project, "&".join(self.field_query)
        )

    def refresh(self):
        """Fill the bug list with new information"""
        self.bugs = processors.bug_count(self.project, **self.query)
        self.save()


class BugCountPlugin(CMSPlugin):
    source = ForeignKey(BugCount)
    low    = IntegerField(_("Low Bug Threshold"), default=10)
    medium = IntegerField(_("Medium Bug Threshold"), default=20)
    high   = IntegerField(_("Height Bug Threshold"), default=50)

    def importance(self):
        c = int(self.source.bugs)
        if c < 0:
            return 'disabled'
        elif c == 0:
            return 'none'
        elif c <= self.low:
            return 'low'
        elif c <= self.medium:
            return 'medium'
        elif c <= self.high:
            return 'high'
        return 'vhigh'

