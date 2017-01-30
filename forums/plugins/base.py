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
Base plugin class
"""

import re
import logging

from os.path import dirname, abspath, join
from dateutil.parser import parse
from collections import defaultdict

from forums.models import Forum

# A dictionary of names -> email addresses
EMAIL_ADDRESSES = defaultdict(set)
FIXTURE_DIR = abspath(join(dirname(__file__), '..', 'fixtures'))

def _parse_address(email):
    name = ''
    for (start, end) in (('<','>'), ('[mailto:', ']')):
        if email and start in email:
            (name, email) = email.split(start, 1)
            email = email.split(end, 1)[0]
    if email and '@' not in email:
        return (email, None)
    return (name.strip(), email.strip())


class BasePlugin(object):
    test_conf = {}

    def __init__(self, key, conf, test=False):
        self.test = test
        self.key = key
        kwargs = dict([(name.lower(), value)
            for name, value in conf.items()
              if name not in ['ENGINE',]
          ])
        self.name = kwargs.pop('name', key.replace('-', ' ').title())
        try:
            self.init(**kwargs)
        except TypeError as err:
            logging.error("Can't load forum plugin: %s (%s)" % (str(err), str(kwargs.keys())))

    def init(self, **kw):
        """Implement this in your plugin to consume configuration values"""
        self.conf = kw

    def sync(self, **kw):
        raise NotImplementedError("Forum plugin '%s' has no sync" % self.name)

    @classmethod
    def kind(cls):
        """Returns the kind of plugin this is (module name)"""
        return cls.__module__.split('.')[-1]


class MessageBase(dict):
    """Provides a standard API to turn a dictionary into a forum message"""
    maps = {
      'reply_id': 'In-Reply-To',
    }

    def __init__(self, data=None):
        if data is not None:
            self.update(data)

    def get(self, key, default=None):
        """Multi-try dictionary get, first look for function overloads get_$key()
           next try the key on the internal dictionary,
           then try the mapped key using maps{}
           finally return the default value"""
        def _dict_get():
            map_key = self.maps.get(key, key.lower())
	    return super(MessageBase, self).get(key,
		     super(MessageBase, self).get(map_key, default))
        return getattr(self, 'get_' + key, _dict_get)()

    def update(self, d):
        """Case insensitive pep8 function name key updater."""
        for key, value in d.items():
            self[key.lower().replace('-', '_')] = value

    def get_all(self):
        """Returns original message and all replies"""
        return [self] + self.get_replies()

    def get_message_id(self):
        return self.get('Message-ID', None)

    def get_reply_id(self):
        return self.get('In-Reply-To', self.get('References', None))

    def get_created(self):
        """Attempt to parse a string as a date"""
        date = self.get('date')
        if isinstance(date, str):
            date = parse(date)
        return date

    def get_data(self):
        return {}

    def get_body(self):
        return self['body'].strip()

    def get_from(self):
        """Returns a tuple of name and email in from address"""
        global EMAIL_ADDRESSES

        for items in ('To', 'CC', 'From'):
            #add_addresses(items)
            for email in self.get(items, '').split(','):
                (name, email) = _parse_address(email)
                if name and email:
                    EMAIL_ADDRESSES[name.lower()].add(email.lower())

        (name, email) = _parse_address(self['From'])
        if email is None and name.lower() in EMAIL_ADDRESSES:
            email = list(EMAIL_ADDRESSES[name.lower()])[0]
        return (name, email)

    def get_email(self):
        return self.get_from()[1]

    def get_username(self):
        return self.get_from()[0]

    def get_user(self):
        """Returns link to a local user based on email address"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        objects = User.objects.filter(email=self.get_email())
        if objects.count() == 1:
            return objects.get()
        objects = User.objects.filter(username=self.get_username())
        if objects.count() == 1:
            return objects.get()
        return None

    def get_userurl(self):
        return ''

    def get_subject(self):
        subject = self['subject']
        for remove in [r'Re:', 'Fw:', r'\[[\w-]+\]']:
            subject = re.sub(remove, '', subject)
        return subject.strip()

