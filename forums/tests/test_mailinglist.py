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
Test the mailing list functionality.
"""
import sys
import inspect

from md5 import md5
from os import unlink
from os.path import dirname, basename, isfile, join

from autotest.base import ExtraTestCase

from django.contrib.auth import get_user_model
from django.utils.text import slugify

from forums.plugins.mailinglist import MailingList


class MailingListTests(ExtraTestCase):
    """Tests for mailing list processing"""
    @classmethod
    def setUpClass(cls):
        super(MailingListTests, cls).setUpClass()
        cls.app_dir = dirname(dirname(inspect.getfile(cls)))
        cls.fixture_dir = join(cls.app_dir, 'fixtures')

    def setUp(self):
        User = get_user_model()
        for pk, user in enumerate([
            ('ted@gould.cx', 'Ted', 'Gould'),
            ('bryce@bryceharrington.org', 'Bryce', 'Harrington')
          ]):
            User.objects.create(pk=pk + 1000,
                username='user-%d' % pk,
                email=user[0],
                first_name=user[1],
                last_name=user[2]
            )

    def test_mailinglist(self):
        """Test full mbox of messages to process"""
        from unittest.case import SkipTest
        raise SkipTest("Incomplete Work")
        mbox = join(self.fixture_dir, 'mailinglist.mbox')
        existing = {}
        ml = MailingList(mbox)
        for message in ml:
            hsh = md5(slugify(message.get_message_id())).hexdigest()[:8]
            self.assertNotIn(hsh, existing, "Collision of mail hash: %s" % hsh)
            existing[hsh] = 1
            with TestMessage(message) as msg:
                self.assertEqual(*msg(join(self.fixture_dir, 'messages', hsh)))


class TestMessage(object):
    def __init__(self, message):
        self.no_file = False
        self.filename = None
        self.message = message

        # XXX Add subject here
        test = self.message.get_part('text/plain')
        #for part in self.message.get_all():
        #    test += "\n---+++---\n%s <%s> (%d) @ %s\n%s" % (
        #        part.get_username(),
        #        part.get_email(),
        #        getattr(part.get_user(), 'pk', -1),
        #        str(part.get('created')),
        #        part.get('body'))
        # XXX Add attachments here
        self.text = test.strip()

    def __enter__(self):
        return self

    def __call__(self, filename):
        self.filename = filename
        try:
            with open(self.filename + '.test', 'r') as fhl:
                return (fhl.read().strip(), self.text)
        except IOError:
            self.no_file = True
            return ('', '')
            raise IOError("Message not found in fixtures.")

    def __exit__(self, exception, tb, *args):
        """Save a backup of the expected text"""
        fn = self.filename + '.run'
        if exception and self.filename is not None or self.no_file:
            sys.stderr.write("Message untested: %s\n" % basename(self.filename))
            with open(fn, 'w') as fhl:
                fhl.write(self.text)
        elif isfile(fn):
            # Remove any previous runs because the test passed
            unlink(fn)

