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

