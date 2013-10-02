#
# Copyright 2013(c) Martin Owens <mail@doctormo.org>
#
# Licensed: AGPLv3
#

from launchpadlib.launchpad import Launchpad

def match(p, ps):
    for (v, n) in ps:
        if n == p or v == p:
            return v
    return None

def bug_count(project, **query):
    lpi = Launchpad.login_anonymously('inkscape-website')
    project = lpi.projects[project]
    if query.has_key('milestone'):
        query['milestone'] = project.getMilestone(name=query['milestone'])
    bugs = project.searchTasks(**query)
    return len(bugs)

#        bugid = unicode(bug).split('/')[-1]
#        bug = Bug.objects.get(bugid=bugid)
#        if not bug:
#            bug = update_bug( bid=bugid )

#
#def update_bug(self, bid=None, bug=None):
#    if not bug and bid:
#        bug = Bug(bugid=bid)
#    if bug:
#        task = launchpad.bugs[bid]
#        bug.bugid   = task.bug.id
#        bug.created = task.bug.date_created
#        bug.updated = task.bug.date_last_updated
#        bug.title   = task.bug.title
#        bug.level   = match(task.importance, LEVELS)
#        bug.status  = match(task.status, STATUS)
#        bug.owner   = task.owner.name
#        bug.save()
#
#        for tag_name in task.bug.tags:
#            tag = Tag.objects.get_or_create(name=tag_name)[0]
#            bug.tags.add(tag)




