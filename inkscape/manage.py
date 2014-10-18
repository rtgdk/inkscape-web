#!/usr/bin/env python
import os
import sys

_VER = "python%d.%d" % (sys.version_info[0], sys.version_info[1])

_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".."))

if __name__ == "__main__":
    sys.path.insert(0, _PATH)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

