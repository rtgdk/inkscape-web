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
Test the plugin syncing
"""

from django.apps import apps
from django.conf import settings

from autotest.base import ExtraTestCase

from forums.models import Forum, Comment
from forums.plugins.base import MessageBase

class PluginTests(ExtraTestCase):
    fixtures = ['test-auth', 'test-contenttype', 'test-forum']
    credentials = dict(username='tester', password='123456')

    def setUp(self):
        super(PluginTests, self).setUp()
        self.forum = Forum.objects.get()

    def sync_message(self, message):
        """Callback function for syncing messages"""
        self.forum.sync_message(message)

    def assertMessages(self):
        """
        Assert that each plugin when syncing with test values, produces EXACTLY
        the same output in the forums/topics/messages objects.
        """
        self.assertEqual(self.forum.topics.count(), 2)
        topics = self.forum.topics.order_by('subject')
        subjects = topics.values_list('subject', flat=True)
        self.assertEqual(tuple(subjects), ('Bublegum is evil', u'Ice king rocks'))

        for topic, messages in zip(topics, [
              ('And you should avoid her.',),
              ('And that\'s a fact!', 'I don\'t agree man.',),
            ]):
            comments = Comment.objects.filter(object_pk=topic.pk)
            msg = comments.values_list('comment', flat=True)
            self.assertEqual(tuple(msg), messages)


FORUM_APP = apps.get_app_config('forums')

for plugin_cls in FORUM_APP.plugins:
    # We make these virtual so we can test each plugin, but reset
    # the database and other states on each run.
    def _test(cls):
        plugin = cls('test', cls.test_conf, test=True)
        def _inner(self):
            """Test plugin sync for """ + plugin.name
            plugin.sync(self.sync_message)
            self.assertMessages()
        return _inner

    setattr(PluginTests, 'test_' + plugin_cls.kind(), _test(plugin_cls))


class MessageTests(ExtraTestCase):
    def test_message(self):
        """Test the message class"""
        class MessageTest(MessageBase):
            maps = {
                'map_a': 'a',
                'map_b': ['a', 'b', 'c'],
                'map_c': ('a', 'b', 'c'),
            }
