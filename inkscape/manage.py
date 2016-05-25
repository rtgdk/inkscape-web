#!/usr/bin/env python
#
# Copyright 2011, Django Project (BSD, generated)
#           2014, Martin Owens <doctormo@gmail.com>
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

import os
import sys

import code, traceback, signal

def debug(sig, frame):
    """Interrupt running process, and provide a python prompt for
    interactive debugging."""
    d={'_frame':frame}         # Allow access to frame object.
    d.update(frame.f_globals)  # Unless shadowed by global
    d.update(frame.f_locals)

    i = code.InteractiveConsole(d)
    message  = "Signal received : entering python shell.\nTraceback:\n"
    message += ''.join(traceback.format_stack(frame))
    i.interact(message)

def listen():
    sys.stderr.write("LISTENING FOR DEBUG\n")
    signal.signal(signal.SIGUSR1, debug)  # Register handler

if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], '..')))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inkscape.settings")

    listen()

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

