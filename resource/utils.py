#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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
#
"""
The MimeType field is actually a fake field, it's just a simple object
created when called with a string version of the mime type.

It converts all the weird and wacky mime types out there into more simple
and segregated forms and provides a way to get icons for them.
"""

import re
import os
import mimetypes

from pygments import highlight, lexers, formatters
from django.utils.safestring import mark_safe
from django.conf import settings
from django.contrib.staticfiles import finders, storage

MIME_DIR = 'mime'
#MIME_URL = os.path.join(settings.STATIC_URL, MIME_DIR)
#MIME_ROOT = os.path.join(settings.STATIC_ROOT, MIME_DIR)

ALL_TEXT_TYPES = dict( (mimes[0], name)
    for (name, alias, patterns, mimes) in lexers.get_all_lexers()
      if mimes ).items()
ALL_TEXT_TYPES.sort(key=lambda a: a[1])

class CodeHtmlFormatter(formatters.HtmlFormatter):

    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        yield 0, '<ol id="lines">'
        for i, t in source:
            yield i, "<li><code>%s</code></li>" % t
        yield 0, '</ol>'


def syntaxer(text, mime):
    """Highlights text files based on their type"""
    formatter = CodeHtmlFormatter(encoding='utf8')
    try:
        lexer = lexers.get_lexer_for_mimetype(str(mime))
    except:
        try:
            lexer = lexers.guess_lexer(text)
        except:
            return text
    return mark_safe(''.join(highlight(text, lexer, formatter)))

def text_count(text):
    num_lines = 0
    num_words = 0
    num_chars = 0
    for line in text.strip().split("\n"):
        words = line.split()
        num_lines += 1
        num_words += len(words)
        num_chars += len(line)
    return (num_lines, num_words)

def coord(n):
    """Removes any units"""
    return int(float(''.join(c for c in n if c in '.0123456789')))

def svg_coords(svg):
    from xml.dom.minidom import parseString, Node
    try:
        doc = parseString(svg.encode('utf-8')).documentElement
        return (coord(doc.getAttribute('width')),
                coord(doc.getAttribute('height')))
    except:
        return (-1,-1)

def upto(d, c='resources', blank=True, lots=False):
    """Quick and easy upload to location"""
    dated = lots and ["%Y","%m"] or []
    return dict(null=blank, blank=blank, upload_to=os.path.join(c, d, *dated))

def cached(f):
    _cname = '_'+f.__name__
    def _inner(self):
        if not hasattr(self, _cname):
            setattr(self, _cname, f(self))
        return getattr(self, _cname)
    return _inner

class MimeType(object):
    tr = {
      'application': {
       'document': ['pdf','rtf','word','powerpoint','excel','spreadsheet','text','presentation','chart'],
       'compressed': ['bzip','zip','gzip','tar'],
       'text': ['xml','plain'],
       'code': ['c++','javascript'],
      },
      'text': {
       'document': ['rtf', 'html'],
       'code': ['python','perl','pascal', 'script', 'tcl', 'shell', 'c-header', 'c', 'c++', 'css','java'],
      }
    }
    s_tr = {
      'compress': 'zip', 'compressed': 'zip', 'bzip2': 'bzip', 'gtar': 'tar', 'gnutar': 'tar',
      'sh': 'shell', 'h': 'c-header', 'cplusplus': 'c++', 'java-source': 'java',
      'mspowerpoint': 'powerpoint', 'msexcel': 'excel', 'msword': 'word',
      'richtext': 'rtf',
    }

    def __init__(self, mime='text/plain', filename=None):
        if filename:
            mime = mimetypes.guess_type(filename, True)[0] or mime
        (self.major, self.minor) = mime.split('/')

    def __str__(self):
        return self.major + "/" + self.minor

    @cached
    def subtype(self):
        """Return the sub-type as a human readable thing"""
        value = self.minor.rsplit('+',1)[0]
        for x in ['x-','script.','vnd.','ms-','windows-','oasis.opendocument.','microsoft.']:
            if value.startswith(x):
                value = value[len(x):]
        return self.s_tr.get(value, value)

    @cached
    def type(self):
        value = self.major
        for x, l in self.tr.get(value, {}).items():
            if self.subtype() in l:
                return x
        return value

    def is_text(self):
        # We test for both because javascript in code and html in document
        return self.type() in ['text', 'code'] or self.major == 'text'

    def is_image(self):
        return self.major == 'image'

    def is_raster(self):
        return self.is_image() and self.minor in ['jpeg', 'gif', 'png']

    def icon(self, subdir=""):
        for ft_icon in [self.subtype(), self.type(), self.minor, self.major]:
            static = os.path.join(MIME_DIR, subdir, ft_icon+'.svg')
            if finders.find(static):
                return storage.staticfiles_storage.url(static)
        return storage.staticfiles_storage.url('mime/unknown.svg')

    def banner(self):
        return self.icon('banner')

VIDEO_URLS = {
  'youtube': r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be/)(watch\?v=|embed/|v/|.+\?v=)?(?P<video_id>[^&=%\?]{11})',
  'vimeo': r'(http:\/\/)?(www\.)?(vimeo\.com)(\/channels\/.+)?\/(?P<video_id>.+)/?',
}

def video_embed(url):
    for site_id, regex in VIDEO_URLS.items():
        match = re.match(regex, url)
        if match:
            return {'type': site_id, 'id': match.group('video_id')}

def hash_verify(sig_type, sig, data):
    import hashlib
    sig.file.open()
    sig.file.seek(0)
    digest = sig.file.read().split(' ')[0].strip()
    hasher = getattr(hashlib, sig_type, hashlib.sha1)()
    for chunk in data.chunks():
        hasher.update(chunk)
    return hasher.hexdigest() == digest

def gpg_verify(user, sig, data):
    import gnupg
    gpg = gnupg.GPG(gnupghome=os.path.join(settings.MEDIA_ROOT, 'gnupg'))
    gpg.import_keys(str(user.details.gpg_key))
    return bool(gpg.verify_file(sig, data.path))

