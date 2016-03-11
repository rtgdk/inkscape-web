#
# Copyright 2016, Martin Owens <doctormo@gmail.com>
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
Provide ways of tracking files in a theme
"""

import os
from collections import defaultdict

from django.conf import settings

from .middleware import RequestMiddleware


class Themer(object):
    """This is a per-request singleton, i.e. completely mad"""
    root = settings.DESIGN_ROOT

    def __new__(cls, *args, **kwargs):
        request = RequestMiddleware.get_request(None)
        if request is None:
            raise KeyError("No request object, thus no theme.")

        if hasattr(request, 'themer'):
            return request.themer

        obj = super(Themer, cls).__new__(request, *args, **kwargs)
        request.themer = obj
        return obj

    def __init__(self, request):
        # We do this to protect new (this isn't the best way to do this)
        if not hasattr(self, 'request'):
            if not os.path.isdir(self.root):
                raise IOError("No design root directory: '%s'." % self.root)
            self.request = request
            self.files = defaultdict(set)
            self.themed = defaultdict(set)

    @property
    def themes(self):
        """Returns an ordered list of theme directories"""
        if self.request.user.is_authenticated():
            return [self.request.user.username, 'default']
        return ['default']

    def file_request(self, kind, filename, path=None):
        # path is when we know the full os path for the requested file
        if path and not os.path.exists(path):
            pass # do something here?
        for theme in self.themes:
            # attempt each file here and reply with a path
            pass

    #def add_template(self, path, theme=None):
    #    """Add a detected template to this request's tracking"""
    #    path = path.strip('/')
    #    self.site_templates.add(path)
    #    if theme is not None:
    #        self.theme_templates[theme].add(path)

    # Also required here is a list of all possible media
     # and all possible templates, so they can requested as extras
      # maybe as an ajax command so we don't rubbish the request with
       # data that's just not required.



