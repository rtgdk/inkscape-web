
import os
from datetime import datetime, timedelta

from . import settings
from . import processors

from django.db.models import Model, CharField, ForeignKey, ManyToManyField,\
                             IntegerField, DateTimeField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from tzinfo import utc


class Project(Model):
    name    = CharField(_('Project Name'), max_length=32)
    lpid    = CharField(_('Launchpad ID'), max_length=64)
    focus   = ForeignKey('Series', null=True, blank=True, related_name="focus")
    updated = DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def refresh(self):
        for series in get_project_series(self.lpid):
            s = Series.objects.get(lpip=series)
            if not s:
                s = Series(lpip=series, project=self, name="-", status="NON")
                s.save()
            s.refresh()

class Series(Model):
    name    = CharField(_('Name'), max_length=32)
    lpid    = CharField(_('Launchpad ID'), max_length=16)
    status  = CharField(_('Status'), max_length=3)
    project = ForeignKey(Project)

    def __unicode__(self):
        return self.name

    def refresh(self):
        for ms in get_series_milestones(self.lpid):
            m = Milestone.objects.get(lpid=ms)
            if not m:
                m = Milestone(lpip=ms, series=self, name=ms.title())
                m.save()
            pass

class Milestone(Model):
    name   = CharField(_('Name'), max_length=32)
    lpid   = CharField(_('Launchpad ID'), max_length=16)
    series = ForeignKey(Series)

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

    tags = CharField(max_length=255, null=True, blank=True,
        help_text=_("Tags to search. To exclude use '-tag' instead."))
    milestone = ManyToManyField(Milestone, null=True, blank=True,
        help_text=_("Show only bug tasks targeted to these milestone."))

    ignore = ['id', 'name', 'bugs', 'project', 'updated']
    tr = { 'tags': 'tag' }

    def __unicode__(self):
        return self.name

    def count(self):
        """Returns the count, may cause a blocking launchpad request"""
        threshold = datetime.now().replace(tzinfo=utc) - timedelta(hours=6)
        if self.bugs == -1 or not self.updated or self.updated < threshold:
            self.refresh()
        return self.bugs

    @property
    def query(self):
        """Returns a launchpad query based on available fields"""
        result = {}
        for name in self._meta.get_all_field_names():
            if name not in self.ignore and hasattr(self, name):
                field = getattr(self, name)
                if field and unicode(field):
                 [name] = unicode(field)
        return result

    @property
    def field_query(self):
        for (name, value) in self.query.iteritems():
            name = self.tr.get(name, name)
            if isinstance(value, list):
                for v in value:
                    yield "field.%s%%3Alist=%s" % (name, v)
            else:
                yield "field.%s=%s" % (name, value)

    def link(self):
        """Tries to return a generated link"""
        return "https://bugs.launchpad.net/%s/+bugs?orderby=-importance&%s" % (
            self.project, "&".join(self.field_query))

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

