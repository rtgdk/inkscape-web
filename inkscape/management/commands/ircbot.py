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

import sys

from easyirc.client.bot import BotClient
from settings import SITE_ROOT

from django.core.management.base import BaseCommand, CommandError
from person.models import UserDetails
from alerts.models import Message

class Command(BaseCommand):
    help = 'Starts an irc bot that will join the main channel and interact with the website.'

    def register_all(self, d):
        for name, func in d.items():
            if callable(func) and name.startswith('on_'):
                print "Hooking up: %s" % func.__doc__
                func = getattr(self, name)
                self.client.events.msgregex.hookback(func.__doc__)(func)

    def on_whois(self, context, message, address, nick):
        """^(\w+)[:\- ]*whois (\w+)"""
        if self.nick != address:
            return
        users = UserDetails.objects.filter(ircnick__iexact=nick)
        if users.count() > 0:
            return context.nick + ': ' + '\n'.join([u"%s - %s/%s" %
              (str(profile.user), SITE_ROOT, profile.user.get_absolute_url())
              for profile in users])
        return context.nick + ': No user with irc nickname "%s" on the website.' % nick

    def on_tell(self, context, message, address, nick, body):
        """^(\w+)[:\- ]*tell (\w+) (.+)$"""
        if self.nick != address:
            return

        from_user = UserDetails.objects.filter(ircnick__iexact=context.nick)
        if from_user.count() != 1:
            return u'Your irc nickname must be configured on the website. Or it must be the only user with this irc nickname.'

        to_user = UserDetails.objects.filter(ircnick__iexact=nick)
        if to_user.count() > 1:
            return u'Too many users have that irc nickname configured.'
        elif to_user.count() == 0:
            return u'Can not find user with irc nickname "%s"' % nick
        
        message = Message.objects.create(subject="From IRC", body=body,
                     sender=from_user.get().user, recipient=to_user.get().user)

        return u'%s: Message Sent' % context.nick

    def go_backward(self, message):
        """
        it would be nice if we could tie into alerts here so they appear on the irc channel
        which could mean some admin alerts for things like cms page edits or it might mean
        personal messages in the case of users.
        """
        pass # XXX Feature Future Request!

    @property
    def nick(self):
        return self.client.connections[0].tried_nick

    def handle(self, *args, **options):
        self.client = BotClient()
        self.register_all(type(self).__dict__)
        self.client.start()

