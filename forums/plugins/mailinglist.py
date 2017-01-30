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
Base utilities for downloading, parsing and breaking apart a mailing list
and it's messages.
"""
import os
import re
import atexit
import logging
import subprocess

from datetime import datetime
from dateutil.parser import parse
from collections import defaultdict

from mailbox import PortableUnixMailbox

from email import message_from_file
from email.Errors import MessageParseError
from email.message import Message as BaseMessage

from forums.plugins.base import BasePlugin, MessageBase, FIXTURE_DIR

# A dictionary of names -> email addresses
EMAIL_ADDRESSES = defaultdict(set)

class MailingList(object):
    def __init__(self, mbox_path, test=False):
        if not test and 'test' in mbox_path:
            raise IOError("Got a test without test: %s" % str(mbox_path))
        self.test = test
        self.path = mbox_path
        self.dest = os.path.dirname(self.path)
        if not os.path.isdir(self.dest):
            raise IOError("Directory missing: %s" % self.dest)
        if not test:
            atexit.register(self.set_position)

    def sync(self, url, user, pwd):
        """Sync the mailbox with the online source"""
        cmd = ['wget', url,
            '--user=' + user,
            '--password=' + pwd,
            '--continue',
            '-O', self.path,
            '-o', '/dev/null'
          ]
        process = subprocess.Popen(cmd)
        process.wait()

    def get_mailbox(self, position=None):
        if not hasattr(self, '_mailbox'):
            self._fp = open(self.path, 'r')
            self._mailbox = PortableUnixMailbox(self._fp, Message)
        if position:
            self._mailbox.seekp = position
        return self._mailbox

    def __iter__(self):
        """Loop through the mbox to find the right messages"""
        for message in self.get_mailbox(0):
            if message is None:
                break
            yield message

    def new_messages(self):
        """Only returns the messages since last run"""
        mailbox = self.get_mailbox(self.get_position())
        for message in mailbox:
            yield message
        if not self.test:
            self.set_position()

    @property
    def position_file(self):
        return self.path[:-4] + 'pos'

    def get_position(self):
        """Returns the last seek location for the mbox"""
        if os.path.isfile(self.position_file):
            with open(self.position_file, 'r') as position_handle:
                return int(position_handle.read())
        return 0

    def set_position(self):
        """Track how far into the mbox we've gotten"""
        try:
            with open(self.position_file, 'w') as position_handle:
                position_handle.write(str(self.get_mailbox().seekp))
        except IOError:
            pass

    def get_delta_size(self):
        """Returns the difference between the last size and the new size"""
        return os.path.getsize(self.path) - self.get_position()


class EmailDeepWell(list):
    """
    Process an email message (text body) into multiple replies.

    Each reply is a previous message with an author and date/time.
    """

    #
    # Inline regexes match replies which are inlined into the message and often
    # encourage bottom and interleaved posting.
    #
    _INLINE = [
      r'On\s(?P<date>\d+-\d+-\d+) (?P<time>\d+:\d+), (?P<user>.+) wrote:',
      r'On\s(?P<date>(\w+,)? \w+ \d+, \d+) at (?P<time>\d+:\d+(:\d+)?(\w\w)?( [+-]\d+)?), (?P<user>.+) wrote:',
      r'On\s(?P<date>\w+ \d+, \d+), at (?P<time>\d+:\d+ (AM|PM)), (?P<user>.+) wrote:',
      r'On\s(?P<date>\w+, \d+-\d+-\d+) at (?P<time>\d+:\d+(:\d+)?(\w\w)?( [+-]\d+)?), (?P<user>.+) wrote:',
      r'On\s(?P<date>\w{3}, \d{1,2} \w{3} \d{4}) (?P<time>\d{2}:\d{2}:\d{2} [+-]\d{4})( \(\w+\))?, (?P<user>.+) wrote:',
      r'On\s(?P<date>\w{3}, \d{1,2} \w{3} \d{4}), (?P<user>.+) wrote:',
      r'(?P<user>.+) wrote:',
    ]
    INLINE_REGEX = ['[\n\.]' + x + '(?P<suffix>\n+>\s*)' for x in _INLINE]
    
    #
    # Seperator regexes match replies which are always at the bottom where top posting
    # is required, they contain a subset rfc822 email headers of the replied message.
    #
    SEPERATOR_REGEX = [
      r'\n-{2,} Forwarded message from (?P<user>.*) -{2,}\n(?P<body>(.|\n)*)\n-{2,} End forwarded message -{2,}\n',
      r'\n-{2,} Forwarded Message -{2,}\n(?P<body>(.|\n)*)',
      # Sometimes original message format has people bottom posting by adding dashes as a seperator.
      r'\n-{2,}\s*Original Message\s*-{2,}\n(?P<body>(.|\n)*)\n-{2,}\n',
      r'\n-{2,}\s*Original Message\s*-{2,}\n(?P<body>(.|\n)*)\n',
    ]

    def __init__(self, text):
        for reply in self._process_part(text.replace('\r\n', '\n')):
            self.insert(0, reply)

    def _next_match(self, rexes, text):
        """Returns the first match from the list of regular expressions"""
        text = '\n' + text + '\n'
        for rex in rexes:
            for match in re.finditer(rex, text):
                data = match.groupdict()
                replace = data.pop('suffix', '\n')
                text = text[:match.start()] + replace + text[match.end():]
                return data, text
        return None, text.strip('\n')

    def _process_part(self, part, **kwargs):
        # a. Find any --- Original Message -- type sections
        data, part = self._next_match(self.SEPERATOR_REGEX, part)
        if data:
            # a1. If any, seperate out the body from the regex group
            body = data.pop('body')
            if '\n\n' in body:
                (head, body) = body.split('\n\n', 1)
            else:
                head = body
            # a2. Parse and add any rfc822 headers on the first lines and remove from body
            heads = dict(line.split(':', 1) for line in head.split('\n') if ':' in line)
            # a3. Combine parsed headers with regex group into a dictionary
            kw = {
                'user': heads.get('From', None),
                'created': heads.get('Date', None),
            }
            kw.update(data)
            # a4. Run the body back through a. for sub-replies
            for reply in self._process_part(body, **kw):
                # a5. Save author and creation date time from the combined dictionary
                yield reply

        # b. Find any 'something wrote:' style comments with ceverons.
        data, part = self._next_match(self.INLINE_REGEX, part)
        #print data
        if data:
            lines = part.replace('=20', '').split("\n")
            (a, b) = ([], [])

            # b1. Seperate out any line with a ceveron, remove a SINGLE ceveron form the body
            nix_line = False
            for line in lines:
                if line.startswith('>'):
                    #print "B LINE: '%s'" % str(line)
                    b.append(line[1:].strip(' '))
                    nix_line = line.endswith('=')
                    continue
                if nix_line:
                    # Some emails have odd ways of saying "the next line wraps" and pu=
                    # t an equals sign right in the middle of a word.
                    nix_line = False
                    if len(line) < 10:
                        b[-1] = b[-1][:-1] + line
                        continue
                #print "A LINE: '%s'" % str(line)
                a.append(line.strip(' '))

            part = "\n".join(a)

            # b2. Run the body back through a. for sub-replies
            for reply in self._process_part("\n".join(b), **data):
                # b3. Save any author and creation date time from the regex group
                yield reply

        yield ReplyMessage(part, **kwargs)


class Message(BaseMessage, MessageBase):
    """
    Provide a replacement class for email.message.Message used
    in mailbox loading which can be fed directly into a Forum sync
    """

    def __init__(self, fp=None):
        self.range = [fp._start, fp._stop]
        self.fp = fp
        self.ok = False
        try:
            message_from_file(fp, self)
        except MessageParseError:
            pass

    def __call__(self):
        if self.ok:
            return BaseMessage()
        BaseMessage.__init__(self)
        self.ok = True
        return self

    def get_data(self):
        """Extra data stored as json used to cache or identify the source"""
        return {
          'file_loc': self.range,
        }

    def get_body(self):
        """Returns the first reply only"""
        return self.get_replies(first=True)[0].get_body()

    def get_part(self, content_type='text/plain', part=None):
        """Can return the specific payload if specified."""
        if part is None:
            part = self

        if part.is_multipart():
            for subpart in part.get_payload():
                ret = self.get_part(content_type, subpart)
                if ret is not None:
                    return ret

        if part.get_content_type() == content_type:
            return part.get_payload()

        return None

    def get_replies(self, first=False):
        """Generator for replies as given by deepwell"""
        body = self.get_part('text/plain')
        if body is not None:
            well = EmailDeepWell(body)
        else:
            # We could look for a html message here to strip down
            well = [ReplyMessage('No text body found')]
        return well[not first:]


class ReplyMessage(MessageBase):
    """A single reply message object"""
    def __init__(self, body, user=None, time=None, date=None, created=None):
        if not isinstance(body, str):
            raise TypeError("Body must be a string")

        # Some messages have horrid adverts at the end, take them off.
        body = re.split('\n-{5,}\n', body)[0]

        # Some messages end up with tripple spacing, remove them.
        self['body'] = body.replace('\n\n\n', '\n\n')
        self['From'] = user
        self['date'] = created

        if created:
            self['date'] = created

        if date and time and not created:
            self['date'] = datetime.combine(parse(date).date(), parse(time).time())


class Plugin(BasePlugin):
    test_conf = {
      'filename': os.path.join(FIXTURE_DIR, 'test.mbox'),
    }

    def init(self, filename, url=None, user=None, password=None):
        self.web_sync = None
        if url is not None:
            # Save the sync from the internet for later.
            self.web_sync = dict(url=url, user=user, password=password)

            # Make sure the filename has a directory to land into (if url sync)
            dest = os.path.dirname(filename)
            if not os.path.isdir(dest):
                os.makedirs(dest)

        try:
            self.ml = MailingList(filename, test=self.test)
        except IOError as err:
            raise KeyError(str(err))

    def sync(self, callback):
        """Sync this mailing list"""
        if self.web_sync:
            self.ml.sync(**self.web_sync)
        delta = self.ml.get_delta_size()

        if delta:
            logging.info(" - %d bytes of new messages found" % delta)
        else:
            logging.info(" - no new messages")

        for message in self.ml.new_messages():
            logging.info(" * Message %s (%s)" % (message.get_message_id(), str(message.get_created())))

            # Add every NEW message to the forum via the callback function
            callback(message)

