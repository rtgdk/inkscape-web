# -*- coding: utf-8 -*-
#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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
Load inkscape docs from the disk and give to the user.
"""
import re
import os
import codecs

from django.http import Http404
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from django.conf import settings

DOC_ROOT = os.path.join(settings.MEDIA_ROOT, 'doc')

def get_redirects():
    """We want to open up a redirects files with all the right
       Instructions, but this mustn't break the site if they fail."""
    if os.path.isdir(DOC_ROOT):
        _file = os.path.join(DOC_ROOT, 'redirects.re')
        if os.path.isfile(_file):
            with open(_file, 'r') as fhl:
                return [ line.strip().split("|") for line in fhl.readlines() ]
    return []

def get_path(uri, check=True):
    path = os.path.join(DOC_ROOT, uri)
    if not os.path.isfile(path):
        # Cheeky asserts return for redirects
        assert check
        for (regex, new_uri) in get_redirects():
            try:
                ret = re.findall(regex, uri)
                assert ret
                return get_path(new_uri % ret[0], False)
            except (Http404, AssertionError):
                # We capture all exceptions to protect from broken regexs
                pass
        raise Http404
    return (path, uri)

def page(request, uri):
    (path, uri) = get_path(uri)
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
        content = content.replace('src="http','|src|')\
            .replace('src="', 'src="%s/' % os.path.join(settings.MEDIA_URL,
              'doc', *uri.split('/')[:-1]))\
            .replace('|src|', 'src="http')
    c = {
        'title': title,
        'content': content,
    }
    return render_to_response('docs/page.html', c,
        context_instance=RequestContext(request))


