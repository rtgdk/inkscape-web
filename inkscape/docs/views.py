# -*- coding: utf-8 -*-
#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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
Load inkscape docs from the disk and give to the user.
"""
import os
import sys
import codecs

from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from inkscape.settings import STATIC_ROOT, DESIGN_URL

def get_path(uri):
    path = os.path.join(STATIC_ROOT, 'doc', uri)
    if not os.path.exists(path):
        sys.stderr.write("Can't find doc '%s'\n" % path)
        raise Http404
    return path

def page(request, uri):
    path = get_path(uri)
    if os.path.isdir(path) or path[-5:] != '.html':
        raise Http404

    with codecs.open(path, "r", "utf-8") as fhl:
        content = fhl.read()
        title = content.split('<title>',1)[-1].split('</title>',1)[0]
        if '<div id="content">' in content:
            content = content.split('<div id="content">',1)[-1]
        elif '<div id="preface">' in content:
            content = content.split('<div id="preface">',1)[-1]
        content = content.split('<div id="footer">')[0]
        content = content.replace('src="', 'src="%s/' % os.path.join(DESIGN_URL, 'doc', *uri.split('/')[:-1]))
    c = {
        'title': title,
        'content': content,
    }
    return render_to_response('docs/page.html', c,
        context_instance=RequestContext(request))


