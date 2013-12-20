
import os
from datetime import datetime, timedelta

from . import settings
from . import processors

from django.db.models import Model, BooleanField, IntegerField,\
      CharField, ForeignKey, ManyToManyField, DateTimeField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from tzinfo import utc

def clean(iterA):
    """Return a list of cleaned items, removes None and '' blank items."""
    for item in iterA:
        if item:
            if isinstance(item, tuple) and len(item) == 2:
                if item[1]:
                    yield item
            elif item:
                yield item


class LpModel(Model):
    updated = DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get(cls, uri, **kwargs):
        """With return the item using the launchpad id, None if not existing OR
           will create the item using the extra data provided in kwargs if added"""
        lpid = str(uri).split('/')[-1]
        result = cls.objects.filter(lpid=lpid)
        if result or not kwargs:
            return result[0] or None
        return cls(lpid=lpid, **kwargs)

    def __unicode__(self):
        return self.name


class Project(LpModel):
    name    = CharField(_('Project Name'), max_length=32)
    lpid    = CharField(_('Launchpad ID'), max_length=64)
    focus   = ForeignKey('Series', null=True, blank=True, related_name="focus")

    def lp_object(self):
        return processors.launchpad().projects[self.lpid]

    def refresh(self):
        for series in self.lp_object().series:
            s = Series.get(series, project=self, name=series.name)
            s.status = series.status
            s.save()
            s.refresh()
        self.focus = Series.get(self.lp_object().development_focus)
        self.save()


class Series(LpModel):
    name    = CharField(_('Name'), max_length=32)
    lpid    = CharField(_('Launchpad ID'), max_length=16)
    status  = CharField(_('Status'), max_length=32)
    project = ForeignKey(Project)

    def lp_object(self):
        return self.project.lp_object().getSeries(name=self.lpid)

    def __unicode__(self):
        if self.status in ('Obsolete'):
            return "%s (%s)" % (self.name, self.status)
        return self.name

    def refresh(self):
        for ms in self.lp_object().all_milestones:
            m = Milestone.get(ms, series=self, name=ms.title)
            m.active = ms.is_active
            m.save()


class Milestone(LpModel):
    name   = CharField(_('Name'), max_length=256)
    lpid   = CharField(_('Launchpad ID'), max_length=256)
    intid  = IntegerField(_('Internal Launchpad ID'), null=True, blank=True)
    active = BooleanField(default=True)
    series = ForeignKey(Series)

    def lp_object(self):
        return self.series.project.lp_object().getMilestone(name=self.lpid)


class BugStatus(Model):
    name    = CharField(max_length=32)
    colour  = CharField(max_length=6, default="ffffff")
    meaning = CharField("Meaning in Project", max_length=256, null=True, blank=True)
    def __unicode__(self):
        return self.name


class BugImportance(Model):
    name    = CharField(max_length=32)
    colour  = CharField(max_length=6, default="ffffff")
    meaning = CharField("Meaning in Project", max_length=256, null=True, blank=True)
    def __unicode__(self):
        return self.name


class BugCount(Model):
    """A query which can be run on the launchpad api to get list of bugs"""
    name    = CharField(_('List Name'), max_length=32)
    project = ForeignKey(Project)
    bugs    = IntegerField(default=-1)
    updated = DateTimeField(auto_now=True)

    # Search field entries (should be automatically used)
    created_before  = DateTimeField(blank=True, null=True,
        help_text=_("That were created before the given date."))
    created_since   = DateTimeField(blank=True, null=True,
        help_text=_("That have been created since the given date."))
    modified_since  = DateTimeField(blank=True, null=True,
        help_text=_("That have been modified since the given date."))
    search_text     = CharField(max_length=128, null=True, blank=True,
        help_text=_("Bug ID or search text."))
    linked_branches = CharField(max_length=64, default="Show all bugs",
        choices=(( "Show all bugs", _("All Bugs")),
           ("Show only Bugs with linked Branches", _("Linked Only")),
           ("Show only Bugs without linked Branches", _("Not Linked Only"))
        ), help_text=_("That are or are not linked to branches"))
    omit_duplicates = BooleanField(default=True,
        help_text=_("Omit bugs marked as duplicate."))
    omit_targeted   = BooleanField(default=False,
        help_text=_("Omit bugs targeted to a series."))
    status          = ManyToManyField(BugStatus, null=True, blank=True,
        help_text=_("Only with any of the given status values."))
    importance      = ManyToManyField(BugImportance, null=True, blank=True,
        help_text=_("Only with any of the given importances."))
    tags            = CharField(max_length=255, null=True, blank=True,
        help_text=_("Tags to search. To exclude use '-tag' instead."))
    tags_combinator = CharField(max_length=3, default='Any',
        choices=(('Any',_('Any Selected Tag')),('All',_('All Selected Tags'))),
        help_text=_("Search for any or all of the tags specified."))
    milestone       = ForeignKey(Milestone, null=True, blank=True,
        help_text=_("Only bugs targeted to this milestone."))
    nominated_for   = ForeignKey(Series, null=True, blank=True,
        help_text=_("Only bugs nominated for this series."))

    ignore = ['id', 'name', 'bugs', 'project', 'updated', 'milestone', 'nominated_for']
    tr = { 'tags': 'tag' }

    def __unicode__(self):
        return self.name

    def count(self):
        """Returns the count, may cause a blocking launchpad request"""
        threshold = datetime.now().replace(tzinfo=utc) - timedelta(hours=6)
        if self.bugs == -1 or not self.updated or self.updated < threshold:
            self.refresh()
        return self.bugs

    def query_item(self, field, api=True):
        """Returns a single field item suitable for query"""
        if hasattr(field, 'lp_object') and api:
            return field.lp_object()
        if 'Many' in str(type(field)):
            return [ self.query_item(obj, api) for obj in field.all() ]
        elif isinstance(field, bool):
            return field
        elif field and unicode(field):
            return unicode(field)

    def query(self, api=True):
        """Returns a launchpad query based on available fields"""
        result = {}
        for name in self._meta.get_all_field_names():
            if name not in self.ignore and hasattr(self, name):
                result[name] = self.query_item( getattr(self, name), api )
        return dict( clean( result.iteritems() ) )

    def field_query(self):
        for (name, value) in self.query(api=False).iteritems():
            name = self.tr.get(name, name)
            if name == 'milestone' and value.intid:
                # Milestone is both a list and a weird int id which we have to
                # find manually. Otherwise we raise error and return a bug url.
                value = [ value.intid ]
            elif name == 'milestone':
                raise LinkFailure("IntID for '%s' Unavailable" % str(value))

            if isinstance(value, bool):
                value = value and "on" or None
            if isinstance(value, list) and name:
                for v in value:
                    yield "field.%s%%3Alist=%s" % (name, v)
            elif value and name:
                yield "field.%s=%s" % (name, value)

    def link(self):
        """Tries to return a generated link"""
        try:
            return "https://bugs.launchpad.net/%s/+bugs?orderby=-importance&%s" % (
                self.project, "&".join(self.field_query()))
        except LinkFailure:
            return "https://bugs.launchpad.net/launchpad/+bug/1241875"

    def refresh(self):
        """Fill the bug list with new information"""
        self.bugs = len(self.project.lp_object().searchTasks(**self.query()))
        self.save()


class LinkFailure(KeyError):
    pass


class BugCountPlugin(CMSPlugin):
    source = ForeignKey(BugCount)
    low    = IntegerField(_("Low Bug Threshold"), default=10)
    medium = IntegerField(_("Medium Bug Threshold"), default=20)
    high   = IntegerField(_("High Bug Threshold"), default=50)

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

