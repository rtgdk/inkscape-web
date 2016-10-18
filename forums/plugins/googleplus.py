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
import json
import logging

from apiclient.discovery import build

from django.conf import settings

from forums.plugins.base import BasePlugin, BaseMessage, FIXTURE_DIR


class FakeGoogle(object):
    """For testing the plugin without internet access."""
    comments = lambda self: self
    activities = lambda self: self

    def __init__(self, filename):
        with open(filename, 'r') as fhl:
	    self.data = json.loads(fhl.read())

    def list(self, userId=None, activityId=None, **kw):
        self.store = self.data[userId or activityId]
        return self

    def execute(self):
        return self.store

class TopicMessage(BaseMessage):
    """Translate a google topic into a usable forum message"""
    pass


class Plugin(BasePlugin):
    test_conf = { 
      'user_id': 'test-group',
      'test_data': os.path.join(FIXTURE_DIR, 'google-plus.json'),
    }   

    @classmethod
    def get_service(cls, fake_data):
        if fake_data:
            return FakeGoogle(fake_data)
        if not hasattr(cls, 'service'):
	    try:
		dkey = settings.GOOGLE_DEVELOPER_KEY
	    except AttributeError:
		raise KeyError("No google plus setup for sync. Make sure "
		    "GOOGLE_DEVELOPER_KEY is defined in your settings.py")

	    # This service object is duplicated for each Plugin instance,
	    # there may be a better way of doing it per-class
	    cls.service = build('plus', 'v1', developerKey=dkey)
        return cls.service

    def init(self, user_id, test_data=None):
        self.user_id = user_id
        self.service = self.get_service(test_data)

    def sync(self, callback):
        """Sync this google plus"""
        act = self.service.activities()
        packet = act.list(userId=self.user_id, collection='public').execute()

        for topic in packet['items']:
            topic['title']
            print topic
            continue
            callback(message)



