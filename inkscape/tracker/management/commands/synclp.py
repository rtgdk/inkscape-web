#
# Copyright Martin Owens 2013
#
# AGPLv3
#
"""
Imports launchpad data for local website display
"""

from launchpadlib.launchpad import Launchpad
from inkscape.tracker.models import Bug, Tag, Blueprint, LEVELS, STATUS
from django.core.management.base import BaseCommand, CommandError

import sys

def f(p, ps):
    for (v, n) in ps:
        if n == p or v == p:
            return v
    return None

class Command(BaseCommand):
    args = ''
    help = 'Imports launchpad bugs and blueprints for website display'

    def handle(self, *args, **options):
        lp = Launchpad.login_anonymously('inkscape-website')
        Bug.objects.all().delete()
        Tag.objects.all().delete()
        for bug in lp.projects['inkscape'].searchTasks():
            try:
                self.add_bug(bug)
            except Exception:
                sys.stderr.write("Skipping: %s\n" % unicode(bug))

    def add_bug(self, task):
        cache = Bug()
        cache.bugid   = task.bug.id
        cache.created = task.bug.date_created
        cache.updated = task.bug.date_last_updated
        cache.title   = task.bug.title
        cache.level   = f(task.importance, LEVELS)
        cache.status  = f(task.status, STATUS)
        cache.owner   = task.owner.name
        cache.save()

        for tag_name in task.bug.tags:
            tag = Tag.objects.get_or_create(name=tag_name)[0]
            cache.tags.add(tag)

        sys.stderr.write("Writing: %s\n" % task.bug.id)



