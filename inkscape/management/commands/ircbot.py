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
import sys
import time
import atexit
import signal
import threading

from easyirc.client.bot import BotClient

from django.db.models import Q
from django.db import connection
from django.conf import settings
from django.utils.timezone import now
from django.db.utils import OperationalError
from django.utils.translation import ugettext as _
from django.utils import translation
from django.core.management.base import BaseCommand, CommandError

from person.models import User
from alerts.models import Message, UserAlert
from resources.models import Category

from inkscape.models import HeartBeat

def url(item):
    """Returns the full URL"""
    if hasattr(item, 'get_absolute_url'):
        item = item.get_absolute_url()
    return settings.SITE_ROOT.rstrip('/') + unicode(item)


class BotCommand(object):
    """A bot command decorator class
    
    @BotCommand(directed=True) - A command where webbot needs to be directly asked

    @BotCommand(directed=False) - A piece of text from anybody any any time

    """
    LANGS = [l[0] for l in settings.LANGUAGES]

    def __init__(self, directed=True):
        self.directed = directed

    def __call__(self, func):
        def _inner(inner_self, context, message, *args, **kwargs):
            """Some basic extra filtering for directed commands"""
            if self.directed:
                if context.target.startswith('#'):
                    if not message.startswith(inner_self.nick + ':') \
                      and not message.endswith(inner_self.nick):
                        return

            translation.activate('en')
            connection.close_if_unusable_or_obsolete()
            if context:
                channel_lang = context.target.split('-')[-1]
                users = User.objects.filter(ircnick__iexact=context.ident.nick)
                if users.count() == 1:
                    translation.activate(users[0].language)
                elif channel_lang in self.LANGS:
                    translation.activate(channel_lang)

            try:
                return func(inner_self, context, *args, **kwargs)
            except OperationalError as error:
                if 'gone away' in str(error):
                    return "The database is being naughty, reconnecting..."
                else:
                    return "A database error, hmmm."
            except Exception:
                if context:
                    context.connection.privmsg(context.target, "There was an error")
                raise

        _inner.__doc__ = func.__doc__
        _inner.__name__ = func.__name__
        return _inner


class Command(BaseCommand):
    help = 'Starts an irc bot that will join the main channel and interact with the website.'

    @property
    def nick(self):
        return self.client.connections[0].tried_nick

    def handle(self, *args, **options):
        if not hasattr(settings, 'IRCBOT_PID'):
            print "Please set IRCBOT_PID to a file location to enable bot."
            sys.exit(1)

        with open(settings.IRCBOT_PID, 'w') as pid:
            pid.write(str(os.getpid()))
        atexit.register(lambda: os.unlink(settings.IRCBOT_PID))

        HeartBeat.objects.filter(name="ircbot").delete()
        self.beat = HeartBeat.objects.create(name="ircbot")

        self.last_alert = now()
        signal.signal(signal.SIGUSR1, self.recieve_alert)
        self.client = BotClient()
        self.register_all(type(self).__dict__)
        self.client.start()

        self.log_status("Server Started!", 0)
        drum = 60 # wait for a minute between beats

        while True:
            try:
                time.sleep(drum)
                self.beat.save()
                assert(self.client.connections[0].socket.connected)
            except KeyboardInterrupt:
                self.on_exit(None, 'Keyboard Interrupt')
                for x, conn in enumerate(self.client.connections):
                    if conn.socket.connected:
                        conn.socket.disconnect()
                self.log_status("Keyboard Interrupt", 1)
                drum = 0.1
            except AssertionError:
                threads = [t for t in threading.enumerate() if t.name != 'MainThread' and t.isAlive()]
                print ""
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

    def register_all(self, d):
        for name, func in d.items():
            if callable(func) and name.startswith('on_'):
                print "Hooking up: %s" % func.__name__
                func = getattr(self, name)
                self.client.events.msgregex.hookback(func.__doc__)(func)

    @BotCommand(False)
    def on_exit(self, context):
        """The trouble with having an open mind, of course, is that people will insist on coming along and trying to put things in it."""
        if context and context.ident:
            self.log_status("Told to quit by: " + context.ident.nick, 2)
        try:
            self.client.quit()
        except Exception as error:
            print "Error quitting: %s" % str(error)

    @BotCommand()
    def on_hello(self, context):
        """Hello"""
        return _("Hello there %(nick)s") % {'nick': context.ident.nick}

    @BotCommand()
    def on_dump(self, context):
        """DumpInfo"""
        context.connection.privmsg(context.ident.nick, "Info: " + \
          ', ident:' + context.ident + \
          ', nick:' + context.ident.nick + \
          ', username:' + context.ident.username + \
          ', host:' + context.ident.host + \
          ', msgtype:' + context.msgtype + \
          ', target:' + context.target
          )

    @BotCommand()
    def on_whois(self, context, nick):
        """whois (\w+)"""
        users = User.objects.filter(Q(ircnick__iexact=nick) | Q(username__iexact=nick))
        if users.count() > 0:
            return context.nick + ': ' + '\n'.join([u"%s - %s" %
              (str(profile), url(profile)) for profile in users])

        return context.nick + ': ' + _(u'No user with irc nickname "%(nick)s" on the website.') % {'nick': nick}

    @BotCommand()
    def on_tell(self, context, nick, body):
        """tell (\w+) (.+)$"""
        from_user = User.objects.filter(ircnick__iexact=context.nick)
        if from_user.count() != 1:
            return _(u'Your irc nickname must be configured on the website. '
                      'Or it must be the only user with this irc nickname.')

        to_user = User.objects.filter(ircnick__iexact=nick)
        if to_user.count() > 1:
            return _(u'Too many users have that irc nickname configured.')
        elif to_user.count() == 0:
            return _(u'Can not find user with irc nickname "%(nick)s"') % {'nick': nick}
        
        message = Message.objects.create(subject="From IRC", body=body,
                     sender=from_user.get(), recipient=to_user.get())

        return u'%s: ' % context.nick + _('Message Sent')

    @BotCommand()
    def on_art(self, context):
        """Get Latest Art"""
        try:
            artworks = Category.objects.get(name='Artwork')
        except Category.DoesNotExist:
            return "No Artworks Category on website"

        try:
            art = artworks.items.filter(published=True).latest('created')
        except Resource.DoesNotExist:
            return "No Artworks uploaded yet"

        return u"%s by %s: %s" % (unicode(art), unicode(art.user), url(art))

    def recieve_alert(self, signum, frame):
        """
        When an alert is created, we dispatch the alert to the user on irc if they are available.
        """
        for alert in UserAlert.objects.filter(created__gt=self.last_alert):
            self.last_alert = now()
            user = alert.user
            nick = user.ircnick
            if not nick:
                continue
            translation.activate(user.language or 'en')
            self.client.privmsg(nick,
              _("ALERT: %(subject)s ... More info: %(url)s") % {
                'subject': alert.subject,
                'url': url(alert.get_absolute_url()),
              }
            )


