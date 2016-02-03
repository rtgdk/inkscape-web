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
Provides django-cms + reversion with per-revision diff data (cached)
"""

__all__ = ('RevisionDiff',)

import os
import sys

from django.db.models import *
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.timezone import now
from django.utils.text import slugify
from django.utils.html import strip_tags, strip_spaces_between_tags, linebreaks

from pile.fields import AutoOneToOneField

from reversion import get_for_object
from reversion.models import Version, Revision, UserModel


null = dict(null=True, blank=True)

FIELD_TEMPLATE = """<tr class="del">
  <th scope='row' rowspan='2'>%s</th>
  <td>-</td>
  <td>%s</td>
</tr><tr class="ins">
  <td>+</td>
  <td>%s</td>
</tr>
"""

try:
    from diff_match_patch import diff_match_patch
except ImportError:
    generate_diffs = None
    Revision.has_diffs = False
else:
    differ = diff_match_patch()
    Revision.has_diffs = True

def clean_text(text):
    return strip_tags(force_text(text)).replace("\n\n\n", "\n\n").strip()

class RevisionDiff(Model):
    revision = AutoOneToOneField(Revision, related_name='diff', **null)
    content  = TextField()
    stub     = TextField(**null)

    # We use these to record details from the revision, in case it's
    # deleted at some point and we should record them.
    user     = ForeignKey(UserModel, **null)
    comment  = TextField(**null)

    # When edited revisions get deleted, we try and preserve
    # The diff and reattach to available 'published' revisions.
    revisions = ManyToManyField(Revision, related_name='diffs', blank=True)

    def __str__(self):
        if self.revision:
            return "Diff for Revison:pk%d" % (self.revision.pk)
        return "Orphaned Diff: %s" % (self.comment or '?')

    def get_absolute_url(self):
        return reverse('cms.diff', kwargs={'pk':self.pk})

    def save(self, **kwargs):
        if not self.content and Revision.has_diffs:
            self.refresh_diff()
        try:
            super(RevisionDiff, self).save(**kwargs)
        except:
            pass

    @property
    def stub_text(self):
        return self.stub.replace('<span>', '').replace('</span>', '\n\n')\
            .replace('<del style="background:#ffe6e6;">', '-->').replace('</del>', '<--')\
            .replace('<ins style="background:#e6ffe6;">', '++>').replace('</ins>', '<++')

    def refresh_diff(self):
        revision = self.revision
        if not revision:
            return

        self.user = revision.user
        self.comment = revision.comment

        content = ""
        f_table  = ""
        diffs = []
        for version in revision.version_set.all():
            fields = version.field_dict
            previous = getattr(version.previous, 'field_dict', {})
            for field in set(list(fields) + list(previous)):
                a = clean_text(previous.get(field, ''))
                b = clean_text(fields.get(field, ''))
                if a == b:
                    # Field is the same for this item.
                    continue
                if '\n' not in a and '\n' not in b:
                #    This process is _really_ expensive. (oops)
                #    # Not a multi-line field, consider differently.
                #    if field not in ('changed_date',):
                #        f_table += FIELD_TEMPLATE % (field, a, b)
                    continue
                diff = differ.diff_main(a, b)
                differ.diff_cleanupSemantic(diff)
                diffs += diff
                content += "<div class='system-message'>%s</div>" % differ.diff_prettyHtml(diff).replace('&para;','')
        if f_table:
            content = ("<table>%s</table>" % f_table) + content
        self.content = content
        self.stub = differ.diff_prettyHtml(self.get_segment(diffs)).replace('&para;','')

    def get_segment(self, diffs):
        """Returns the first section of the diff as a stub"""
        size = 1024
        cleaned = self.stem_diff(diffs)
        tot = 0
        for (op, text) in cleaned:
            tot += len(text)
            if tot > size:
                break
            yield (op, text)

    def stem_diff(self, diffs):
        left_size = 10
        right_size = 10
        # First step is to stem non-changed parts with elipsis
        for x, (op, text) in enumerate(diffs):
            if op == 0:
                lines = text.splitlines()
                if len(lines) == 0:
                    continue

                if len(lines) == 1 and len(text) <= left_size + right_size \
                  and x > 0 and x < len(diffs):
                    yield (op, text)
                    continue

                if x > 0:
                    if len(lines[0]) > left_size:
                        yield (op, lines[0][:left_size] + "...")
                    else:
                        yield (op, lines[0])

                if x < len(diffs):
                    if len(lines[-1]) > right_size:
                        yield (op, "..." + lines[-1][-right_size:])
                    else:
                        yield (op, lines[-1])
            else:
                yield (op, text)


