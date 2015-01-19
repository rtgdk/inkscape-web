#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
We're going to monkey patch django-cms until we can get some of these patches live.
"""

from cms.utils import helpers, get_cms_setting
from django.contrib.contenttypes.models import ContentType
from cms.models.pagemodel import Page
from cms.admin.pageadmin import PageAdmin, PUBLISH_COMMENT, is_installed

DRAFT_ID = "DRAFT: "
HISTORY_LIMIT = get_cms_setting("MAX_PAGE_HISTORY_REVERSIONS")



_make_revision_with_plugins = helpers.make_revision_with_plugins
def make_revision_with_plugins(obj, user=None, message=None, draft=True):
    """
    Here we just want to ignore the published revision, it's happend already!
    """
    if message == PUBLISH_COMMENT:
        return False
    if draft:
        message = DRAFT_ID + message
    return _make_revision_with_plugins(obj, user=user, message=message)

helpers.make_revision_with_plugins = make_revision_with_plugins



def create_published_revision(self, page, publish=False):
    """
    We want to delete each of the previous revisions, but copy all their comments.
    We will also remove entries past the max_revision
    """
    if not (publish and is_installed('reversion') and page):
        return False

    from reversion.models import Version, Revision

    content_type = ContentType.objects.get_for_model(Page)
    versions  = Version.objects.filter(content_type=content_type, object_id_int=page.pk)
    revisions = Revision.objects.filter(version__in=versions).distinct()
    drafts    = revisions.filter(comment__startswith=DRAFT_ID)

    # We want to record the users who drafted this change
    # It's in the log we know, but this might be helpful too
    comments = drafts.values_list('comment', 'user__username')
    users = set([ c[1] for c in comments ])
    if len(users) > 1:
        comment = '\n'.join([ "%s: %s" % (c[1], c[0][len(DRAFT_ID):]) for c in comments ])
    else:
        comment = '\n'.join([c[0][ len(DRAFT_ID):] for c in comments ])

    if drafts.count() > 0:
        # XXX In a clean version, user would be passed in
        user = drafts[0].user
        drafts.delete()
        make_revision_with_plugins(page, user, comment, draft=False)

    if HISTORY_LIMIT:
        pks = revisions.order_by('-pk').values_list('pk', flat=True)[:HISTORY_LIMIT]
        revisions.exclude(pk__in=pks).delete()


PageAdmin.cleanup_history = create_published_revision

