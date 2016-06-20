#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
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
We're going to monkey patch django-cms until we can get some of these patches live.
"""

from django.apps import AppConfig
from django.contrib.contenttypes.models import ContentType

from reversion.models import Revision, Version, post_revision_commit
from cms.utils import helpers, get_cms_setting

from .signals import post_revision

DRAFT_ID = "DRAFT: "

_make_revision_with_plugins = helpers.make_revision_with_plugins
def make_revision_with_plugins(obj, user=None, message=None, draft=True):
    # Tag drafts so we can clean them up later
    from cms.admin.pageadmin import PUBLISH_COMMENT
    if draft and message != PUBLISH_COMMENT:
	message = "%(draftid)s%(message)s" % {'draftid':DRAFT_ID, 'message':message}

    _make_revision_with_plugins(obj, user=user, message=message)
helpers.make_revision_with_plugins = make_revision_with_plugins


def new_revision(instances, revision, versions, **kwargs):
    # Is it a new published revision object?
    if revision.comment.startswith(DRAFT_ID):
        return

    try:
        page = revision.page
    except Version.DoesNotExist:
        return # Not a CMS/Page revision

    # We want to record the users who drafted this change
    # It's in the log we know, but this might be helpful too
    drafts = page.revisions.filter(comment__startswith=DRAFT_ID)

    if drafts.count() > 0:
        (comments, users) = zip(*drafts.values_list('comment', 'user__username'))
        comments = [ comment[len(DRAFT_ID):] for comment in comments ]
        if len(set(users)) > 1 or revision.user.username != users[0]:
            revision.comment = '\n'.join(["%s: %s" % cu for cu in zip(users, comments)])
        else:
            revision.comment = '\n'.join(comments)
        revision.save()
        drafts.delete()

    post_revision.send(type(page), instance=page, revision=revision)


def get_previous(self):
    if not hasattr(self, '_previous'):
        qs = type(self).objects.filter(
            object_id_int   = self.object_id_int,
            content_type    = self.content_type,
            revision_id__lt = self.revision.pk
          ).order_by('-pk')[:1]
        if qs.count() == 0:
            self._previous = None
        else:
            self._previous = qs[0]
    return self._previous

def get_previous_revision(self):
    return getattr(self.version_set.all()[0].previous, 'revision', None)

def has_previous(self):
    return self.previous is not None

def cleanup_history(self, page, publish=False):
    if HISTORY_LIMIT and publish:
        page.revisions.order_by('-pk')[HISTORY_LIMIT+1:].delete()

def get_diff(self):
    if not hasattr(self, '_diff'):
        from .utils import RevisionDiff
        previous = self.previous
        pk = previous.pk if previous else 0
        self._diff = RevisionDiff(pk, self.pk)
    return self._diff

class CmsDiffConfig(AppConfig):
    name = 'cmsdiff'

    def ready(self):
        from cms.models import Page

        # We setup a property on any revision to get it's page. This is needed to link
        # the revision back to it's progenitor object and thus to other revisons
        try:
            page_type = ContentType.objects.get_for_model(Page)
        except RuntimeError:
            return # Not setup yet.

        Revision.page = property(lambda self: self.version_set.get(content_type=page_type).object)
        Page.revisions = property(lambda self: Revision.objects.filter(version__content_type=page_type, version__object_id_int=self.pk))
        Page.cleanup_history = cleanup_history

        # Add some navigation properties (useful in templates)
        Version.previous = property(get_previous)
        Revision.previous = property(get_previous_revision)
        Version.has_previous = has_previous
        Revision.has_previous = has_previous
        Revision.diff = get_diff

        # Connect the revision creation signal to deal with drafts
        post_revision_commit.connect(new_revision, dispatch_uid='cmsdiff')


