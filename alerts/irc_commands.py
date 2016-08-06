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
IRC Commands and support for alerts.
"""
import signal

from django.contrib.auth import get_user_model
from django.utils.timezone import now

from inkscape.management.commands.ircbot import BotCommand

from .models import Message, UserAlert

class TellCommand(BotCommand):
    regex = "tell (\w+) (.+)$"

    def run_command(self, nick, body):
        from_user = get_user_model().objects.filter(ircnick__iexact=context.nick)
        if from_user.count() != 1:
            return _(u'Your irc nickname must be configured on the website. '
                      'Or it must be the only user with this irc nickname.')

        to_user = get_user_model().objects.filter(ircnick__iexact=nick)
        if to_user.count() > 1:
            return _(u'Too many users have that irc nickname configured.')
        elif to_user.count() == 0:
            return _(u'Can not find user with irc nickname "%(nick)s"') % {'nick': nick}
    
        message = Message.objects.create(subject="From IRC", body=body,
                     sender=from_user.get(), recipient=to_user.get())

        return u'%s: ' % context.nick + _('Message Sent')


class RecieveAlert(BotCommand):
    """This isn't a command, but a signal waiter from the alerts system"""
    def __init__(self, *args, **kw):
        super(RecieveAlert, self).__init__(*args, **kw)
        self.last_alert = now()
        signal.signal(signal.SIGUSR1, self.recieve_alert)

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


