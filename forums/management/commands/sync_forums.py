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
Sync all configured mailing lists and insert into forums.
"""

import os
import sys
import logging

from django.apps import apps
from django.conf import settings
from django.core.management.base import NoArgsCommand

from forums.models import Forum
from forums.mailinglist import MailingList

#
# Note: There's not support for attachments yet.
#

class Command(NoArgsCommand):
    help = "Run as a cron job every five minutes to sync mbox from mailing list archive"
    option_list = BaseCommand.option_list + ( 
        make_option(
            '--sync',
            action='store',
            dest='name',
            default=None,
            help='Name of the configured sync to perform (default is All).'),
    )  

    def handle(self, name=None):
        app = apps.get_app_config('forums')
        # Select all plugins if not supplied on command line
        try:
            syncs = [app.plugin[name]] if name else app.plugins
        except KeyError:
            logging.error("No plugin called '%s' found" % name)

        for plugin in syncs:
            forums = Forums.objects.filter(sync=key)

            if forums.count() == 0:
                logging.error(" X Not syncing %s, (no forum targets)" % key)
                continue

            def save_messages(self, message):
                """Save messages callback run by plugin.'sync'"""
                for forum in forums:
                    forum.sync_message(message)

            try:
                # Call plugin sync and save the messages.
                plugin.sync(save_messages)
            except (NotImplementedError, KeyError) as err:
                if name:
                    # Only error, if we asked for this plugin on the command line
                    logging.error("Not syncing: %s" % str(err))
                continue
            except Exception as err:
                logging.error("Exception in %s: %s" % (name, str(err)))

