#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
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
Starts an irc bot to join the configured IRC channel.
"""

import os
import time
import atexit
import threading

from importlib import import_module
from easyirc.client.bot import BotClient

from django.db import connection
from django.db.utils import OperationalError

from django.apps import apps
from django.conf import settings

from django.utils import translation
from django.utils.translation import ugettext as _
from django.utils.module_loading import module_has_submodule

from django.core.management.base import BaseCommand, CommandError

from inkscape.models import HeartBeat

def url(item):
    """Returns the full URL"""
    if hasattr(item, 'get_absolute_url'):
        item = item.get_absolute_url()
    return settings.SITE_ROOT.rstrip('/') + unicode(item)

class BotCommand(object):
    """Base class for all commands you want available in irc"""
    LANGS = [l[0] for l in settings.LANGUAGES]
    is_channel = True
    is_direct = True
    regex = []

    @property
    def name(self):
        return type(self).__name__

    @property
    def connection(self):
        return self.caller.connection

    def run_command(self, *args, **kwargs):
        """Called when the regex matches from inputs"""
        raise NotImplementedError("run_command in %s" % type(self).__name__)

    def ready(self):
        """Called when the connection is ready"""
        pass

    def __init__(self, caller):
        self.is_ready = False
        self.caller = caller
        self.client = caller.client
        self.context = None

    def get_language(self):
        """Pick the best language to reply with here, default is 'en'"""
        return 'en'

    def __call__(self, context, message, *args, **kwargs):
        """Some basic extra filtering for directed commands"""
        self.context = context
        if context.target.startswith('#') != self.is_channel:
            print " ! Failing channel"
            return

        if self.is_direct != (
             message.startswith(context.ident.nick + ':') \
             or message.endswith(context.ident.nick)
           ):
            print " ! Failing directness"
            return

        connection.close_if_unusable_or_obsolete()

        try:
	    translation.activate(self.get_language())
            return self.run_command(context, *args, **kwargs)
        except OperationalError as error:
            if 'gone away' in str(error):
                return "The database is being naughty, reconnecting..."
            else:
                return "A database error, hmmm."
        except Exception:
            if context:
                context.connection.privmsg(context.target, "There was an error")
            raise



class Command(BaseCommand):
    help = 'Starts an irc bot that will join the main channel and interact with the website.'

    @property
    def nick(self):
        return self.client.connections[0].tried_nick

    def handle(self, *args, **options):
        if not hasattr(settings, 'IRCBOT_PID'):
            print "Please set IRCBOT_PID to a file location to enable bot."
            return

        with open(settings.IRCBOT_PID, 'w') as pid:
            pid.write(str(os.getpid()))
        atexit.register(lambda: os.unlink(settings.IRCBOT_PID))

        HeartBeat.objects.filter(name="ircbot").delete()
        self.beat = HeartBeat.objects.create(name="ircbot")

        self.client = BotClient()
        self.commands = list(self.load_irc_modules())
        self.client.start()
        self.connection = self.client.connections[0]

        self.log_status("Server Started!", 0)
        drum = 10 # wait for a minute between beats

        while True:
            try:
                time.sleep(drum)
                self.beat.save()
                assert(self.connection.socket.connected)
                self.ready_commands()
            except KeyboardInterrupt:
                self.client.quit()
                for x, conn in enumerate(self.client.connections):
                    if conn.socket.connected:
                        conn.socket.disconnect()
                self.log_status("Keyboard Interrupt", 1)
                drum = 0.1
            except AssertionError:
                threads = [t for t in threading.enumerate() if t.name != 'MainThread' and t.isAlive()]
                for t in threads:
                    # This is for error tracking when treading is messed up
                    self.log_status("Thread Locked: %s (Alive:%s, Daemon:%s)" % (t.name, t.isAlive(), t.isDaemon()), -10)

                if not threads:
                    self.log_status("Socket Disconnected", -1)
                    break
                else:
                    drum = 0.1

    def log_status(self, msg, status=-1):
        print msg
        if self.beat.status == 0:
            self.beat.error = msg
            self.beat.status = status
            self.beat.save()

    def load_irc_modules(self):
        """Generate all BotCommands available in all installed apps"""
        for command in self.load_irc_commands(globals(), 'inkscape.management.commands.ircbot'):
            yield command

        for app_config in apps.app_configs.values():
            app = app_config.module
            if module_has_submodule(app, 'irc_commands'):
                app = app.__name__
                module = import_module("%s.%s" % (app, 'irc_commands'))
                for command in self.load_irc_commands(module.__dict__, module.__name__):
                    yield command

    def load_irc_commands(self, possible, mod):
        """See if this is an item that is a Bot Command"""
        for (name, value) in possible.items():
            if type(value) is type(BotCommand) and \
                 issubclass(value, BotCommand) and \
                 value is not BotCommand and \
                 value.__module__ == mod:
                yield self.register_command(value(self))

    def register_command(self, command):
        """Register a single command class inheriting from BotCommand"""
        print "Hooking up: %s" % command.name
        regexes = command.regex
        if not isinstance(regexes, (list, tuple)):
            regexes = [regexes]
        for regex in regexes:
            self.client.events.msgregex.hookback(regex)(command)
        return command

    def ready_commands(self):
        """Make commands ready after we know for sure that we're connected"""
        for command in self.commands:
            try:
                if not command.is_ready:
                    command.is_ready = bool(command.ready())
            except Exception as err:
                print "Error getting %s ready: %s" % (command.name, str(err))


class ExitCommand(BotCommand):
    name = "Exit the IRC Bot"
    regex = """The trouble with having an open mind, of course, is that people will insist on coming along and trying to put things in it."""

    def run_command(self):
        if context and context.ident:
            self.caller.log_status("Told to quit by: " + context.ident.nick, 2)
        try:
            self.client.quit()
        except Exception as error:
            print "Error quitting: %s" % str(error)

class HelloCommand(BotCommand):
    regex = [
      "Hello", "Allo", "Bonjour",
    ]
    def run_command(self):
        """Hello"""
        return _("Hello there %(nick)s") % {'nick': context.ident.nick}

class DumpCommand(BotCommand):
    regex = "DumpInfo"
    def run_command(self):
        """DumpInfo"""
        self.context.connection.privmsg(context.ident.nick, "Info: " + \
          ', ident:' + context.ident + \
          ', nick:' + context.ident.nick + \
          ', username:' + context.ident.username + \
          ', host:' + context.ident.host + \
          ', msgtype:' + context.msgtype + \
          ', target:' + context.target
          )

