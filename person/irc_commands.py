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
Commands related to Users and Teams
"""

from django.db.models import Q
from django.db.models.signals import post_save

from inkscape.management.commands.ircbot import BotCommand

from .models import User, Team, TeamChatRoom

class WhoisCommand(BotCommand):
    regex = "whois (\w+)"

    def run_command(self, nick):
        users = User.objects.filter(Q(ircnick__iexact=nick) | Q(username__iexact=nick))
        if users.count() > 0:
            return context.nick + ': ' + '\n'.join([u"%s - %s" %
              (str(profile), url(profile)) for profile in users])

        return context.nick + ': ' + _(u'No user with irc nickname "%(nick)s" on the website.') % {'nick': nick}

class TeamChannels(BotCommand):
    def ready(self):
        post_save.connect(self.update, sender=Team)
        self.update()

    def update(self, *args, **kw):
        rooms = self.connection.channels.keys()
        for chatroom in TeamChatRoom.objects.all():
            if '#' + chatroom.channel not in rooms:
                self.connection.join('#' + chatroom.channel)
                return False
        return True

        #if self.context is not None:
        #    channel_lang = context.target.split('-')[-1]
        #    users = User.objects.filter(ircnick__iexact=context.ident.nick)
        #    if users.count() == 1:
        #        translation.activate(users[0].language)
        #    elif channel_lang in self.LANGS:
        #        translation.activate(channel_lang)

