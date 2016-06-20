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
"""

from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import strip_tags, strip_spaces_between_tags, linebreaks

from reversion.models import Version, Revision, UserModel

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

def stub_html(stub):
    """Returns a html of the stub text"""
    return stub.replace('<span>', '').replace('</span>', '\n\n')\
        .replace('<del style="background:#ffe6e6;">', '-->').replace('</del>', '<--')\
        .replace('<ins style="background:#e6ffe6;">', '++>').replace('</ins>', '<++')

def get_vid(version):
    """Returns a version id unique to this item"""
    return "%s-%s" % (version.content_type_id, version.object_id)

def versions_dict(revision):
    """Returns a dictionary of versions in this revision"""
    return dict(
      (get_vid(version), version_dict(version))
        for version in revision.version_set.filter()
    )

def version_dict(version):
    """Get version dictionary WITHOUT parent objects"""
    try:
        object_version = version.object_version
    except IndexError as err:
        return {}
    obj = object_version.object
    result = {}
    for field in obj._meta.fields:
	result[field.name] = field.value_from_object(obj)
    result.update(object_version.m2m_data)
    return result


class RevisionDiff(object):
    def __init__(self, from_id, to_id):
        self.from_revision = Revision.objects.get(pk=from_id)
        self.to_revision = Revision.objects.get(pk=to_id)

        self.from_versions = versions_dict(self.from_revision)
        self.to_versions = versions_dict(self.to_revision)

        # Store changes to non-body fields
        self.fields = {}

        # Map plugins to their bodies
        self.plugins = {}

        # Map languages to pages
        self.pages = {}

        self.init()

    @property
    def user(self):
        return self.to_revision.user

    @property
    def comment(self):
        return self.to_revision.comment

    def init(self):
        for (version_id, fields) in self.to_versions.items():
            previous = self.from_versions.pop(version_id, None)
            if previous is None:
                continue
            if 'language' in fields and 'id' in fields:
                self.plugins[fields['id']] = fields
            if 'title' in fields:
                self.pages[fields['language']] = fields
            self.from_versions[version_id] = previous

    def __iter__(self):
        """When looping for all body changes"""
        for (version_id, fields) in self.to_versions.items():
            previous = self.from_versions.pop(version_id, None)
            if previous is None:
                continue

            for field, a, b in self.get_changes(fields, previous):
                yield field, a, b


    def get_changes(self, fields, previous):
        # Loop over every key in fields and previous without duplication.
        for key in set(list(fields) + list(previous)):
            a = clean_text(previous.get(key, ''))
            b = clean_text(fields.get(key, ''))

            # Is field is the same for this item.
            if a == b:
                continue

            # Is this item a regular field.
            if '\n' not in a and '\n' not in b:
                if key not in ('changed_date', 'creation_date',
                        'numchild', 'depth', 'path', 'publisher_public'):
                    yield (key, a, b)
                continue

            diff = differ.diff_main(a, b)
            differ.diff_cleanupSemantic(diff)

            ptr = fields.get('cmsplugin_ptr', None)
            plugin = self.plugins.get(ptr, {})
            page = self.pages.get(plugin.get('language', None), {})

            if 'title' in page:
                yield ('%s (%s)' % (page['title'], plugin['language']), None, None)

            yield (key, differ.diff_prettyHtml(diff).replace('&para;',''), None)


def get_segment(diffs):
    """Returns the first section of the diff as a stub"""
    size = 1024
    cleaned = stem_diff(diffs)
    tot = 0
    for (op, text) in cleaned:
        tot += len(text)
        if tot > size:
            break
        yield (op, text)

def stem_diff(diffs):
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


