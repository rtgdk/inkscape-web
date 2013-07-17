#!/usr/bin/env python

import sys
import os

_VER = "python%d.%d" % (sys.version_info[0], sys.version_info[1])

_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".."))

sys.path.insert(0,os.path.join(_PATH,'pythonenv', 'lib', _VER, 'site-packages'))
sys.path.insert(0,os.path.join(_PATH,'libs'))

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
