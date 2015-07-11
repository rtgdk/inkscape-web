#
# Copyright 2010, Chris Morgan
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
Find and initialize the local_settings.py - this file documents all the
settings and keys which should /NEVER/ be committed to a repository and it
seperates out the sys-admin responsibility from the programmer's.
"""

from shutil import copyfile

import logging
import os

BASE_DIR = os.path.dirname(__file__)
SETTINGS = 'local_settings.py'

try:
  from local_settings import *
except ImportError:
  target = os.path.join(BASE_DIR, SETTINGS)
  if not os.path.exists(target):
      for template in (target + '.template', target[:-3] + '.template'):
          if os.path.exists(template):
              copyfile(template, target)
              break
  try:
      from local_settings import *
  except ImportError:
      logging.error("No settings found and default template failed to load.")
      exit(3)

