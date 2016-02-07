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

from django.utils.timezone import now
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from person.models import User
from alerts.models import Message, UserAlert
from resources.models import Category

def url(item):
    """Returns the full URL"""
    if hasattr(item, 'get_absolute_url'):
        item = item.get_absolute_url()
    return settings.SITE_ROOT.rstrip('/') + unicode(item)


class Command(BaseCommand):
    help = 'Starts an irc bot that will join the main channel and interact with the website.'

    def handle(self, *args, **options):
        if not hasattr(settings, 'IRCBOT_PID'):
            print "Please set IRCBOT_PID to a file location to enable bot."
            sys.exit(1)

        with open(settings.IRCBOT_PID, 'w') as pid:
            pid.write(str(os.getpid()))
        atexit.register(lambda: os.unlink(settings.IRCBOT_PID))

        self.last_alert = now()
        signal.signal(signal.SIGUSR1, self.recieve_alert)
        self.client = BotClient()
        self.register_all(type(self).__dict__)
        self.client.start()

        # Keep ircbot main thread running
        print "Server Started!"
        while True:
            try:
                time.sleep(2)
                assert(self.client.connections[0].socket.connected)
            except KeyboardInterrupt:
                self.on_exit(None, None)
                break
            except AssertionError:
                break

    def register_all(self, d):
        for name, func in d.items():
            if callable(func) and name.startswith('on_'):
                print "Hooking up: %s" % func.__name__
                func = getattr(self, name)
                self.client.events.msgregex.hookback(func.__doc__)(func)

    def on_exit(self, context, message):
        """The trouble with having an open mind, of course, is that people will insist on coming along and trying to put things in it."""
        print "Bot is going to sleep!"
        try:
            self.client.quit()
        except:
            pass
        self.client.connections[0].socket.disconnect()

    def on_whois(self, context, message, address, nick):
        """^(\w+)[:\- ]*whois (\w+)"""
        if self.nick != address:
            return
        users = User.objects.filter(ircnick__iexact=nick)
        if users.count() > 0:
            return context.nick + ': ' + '\n'.join([u"%s - %s" %
              (str(profile), url(profile)) for profile in users])
        return context.nick + ': No user with irc nickname "%s" on the website.' % nick

    def on_tell(self, context, message, address, nick, body):
        """^(\w+)[:\- ]*tell (\w+) (.+)$"""
        if self.nick != address:
            return

        from_user = User.objects.filter(ircnick__iexact=context.nick)
        if from_user.count() != 1:
            return u'Your irc nickname must be configured on the website. Or it must be the only user with this irc nickname.'

        to_user = User.objects.filter(ircnick__iexact=nick)
        if to_user.count() > 1:
            return u'Too many users have that irc nickname configured.'
        elif to_user.count() == 0:
            return u'Can not find user with irc nickname "%s"' % nick
        
        message = Message.objects.create(subject="From IRC", body=body,
                     sender=from_user.get(), recipient=to_user.get())

        return u'%s: Message Sent' % context.nick

    def on_art(self, context, message):
        """Get Latest Art"""
        cat = Category.object.filter(name='Artwork')
        if cat.count() < 1:
            return
        item = cat.items.filter(visible=True).latest('-created')
        return u"%s by %s: %s" % (unicode(item), unicode(item.user), url(item))

    def recieve_alert(self, signum, frame):
        """
        When an alert is created, we dispatch the alert to the user on irc if they are available.
        """
        for alert in UserAlert.objects.filter(created__gt=self.last_alert):
            self.last_alert = now()
            user = alert.user
            nick = user.ircnick
            if nick:
                self.client.privmsg(nick, "ALERT: %s ... More info: %s" % (alert.subject, alert.get_absolute_url()))

    @property
    def nick(self):
        return self.client.connections[0].tried_nick


