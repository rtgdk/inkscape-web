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
Creates a template loader for serving designer-edited pages.
"""

import sys
import os

from django.conf import settings
from django.utils._os import safe_join
from django.core.exceptions import SuspiciousFileOperation
from django.template.loaders.filesystem import Loader as BaseLoader

from .themer import Themer

def get_path(path):
    """Makes a path if needed"""
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except OSError:
            pass
    return path

DR = settings.DESIGN_ROOT

class Loader(BaseLoader):
    """
    Allows templates to be loaded from a theme design directory.
    """
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Return the next nearest designer template.
        """
        try:
            themer = Themer()
            for theme in themer.themes:
                if os.path.isfile():
                    themer.add_template(template_name)
                template_dir = os.path.join(DR, theme, 'templates')
                print "TRYING THEME FILE: %s / %s" % (theme, template_name)
                yield safe_join(get_path(template_dir), template_name)
        except KeyError:
            print "No request object? WTF"
            pass
        except SuspiciousFileOperation:
            pass

from django.templatetags.static import StaticNode

OLD_HS = StaticNode.handle_simple

@classmethod
def new_handle_simple(cls, path):
    """Monkey patch in statci theme support"""
    root = DR if settings.DEBUG else settings.STATIC_ROOT

    theme = get_theme()
    if theme is not None:
        #record = getattr(request, 'static_files', set())
        new_path = os.path.join(DR, theme, path)
        if os.path.exists(new_path):
            #record[path]
            path = new_path.replace(root, '')
    sys.stderr.write(" @@ PATH -- %s\n" % str(path))
    return OLD_HS(path)

if settings.STATIC_ROOT in settings.DESIGN_ROOT:
    StaticNode.handle_simple = new_handle_simple
    sys.stderr.write(" ++ Design toolbar completely loaded\n")
else:
    sys.stderr.write(" !! Design toolbar not completely loaded, DESIGN_ROOT "
                     "is not inside STATIC_DIR\n")

