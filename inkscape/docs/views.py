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

from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from inkscape.settings import STATIC_ROOT

def get_path(uri):
    path = os.path.join(STATIC_ROOT, 'doc', uri)
    if not os.path.exists(path):
        sys.stderr.write("Can't find doc '%s'\n" % path)
        raise Http404
    return path

def page(request, uri):
    path = get_path(uri)
    if os.path.isdir(path):
        return index(request, uri)
    with open(path, 'r') as fhl:
        (t, l) = fhl.read().split('<div id="content">')
        content = l.split('<div id="footer">')[0]
        title = t.split('<title>')[-1].split('</title>')[0]
    c = {
        'title': title,
        'content': content,
        'folder': os.path.join('doc', *uri.split('/')),
    }
    return render_to_response('docs/page.html', c,
        context_instance=RequestContext(request))

def index3(request, uri):
    path = get_path(uri)
    if os.path.isfile(path):
        return page(request, uri)
    # Dir here
    c = { 'title': path }
    return render_to_response('docs/index.html', c,
        context_instance=RequestContext(request))


