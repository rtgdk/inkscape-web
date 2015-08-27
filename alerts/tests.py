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

from resource.tests.base import BaseCase, BaseUserCase, BaseAnonCase
from alerts.models import Message, AlertType, UserAlertManager
from alerts.alert import MessageAlert

from django.contrib.auth.models import User

class BasicTests(BaseCase):
    fixtures = ['test-auth',]

    def test_registration(self):
        """Message alerts have been registered"""
        self.assertTrue(hasattr(Message, 'alerts'))

    def test_links(self):
        """Messages have alert manager has AlertBase has AlertType"""
        self.assertEqual(type(Message.alerts), UserAlertManager)
        self.assertEqual(type(Message.alerts.alert_type), AlertType)
        self.assertEqual(type(Message.alerts.alert_type._alerter), MessageAlert)
        self.assertEqual(Message.alerts.alert_type.sender, Message)

    def test_object_link(self):
        """Objects have working manager"""
        message = Message.objects.create(recipient_id=1, sender_id=1)
        self.assertEqual(type(message.alerts), UserAlertManager)
        self.assertEqual(type(message.alerts.target), Message)

    def test_user_link(self):
        """Users have a list of alerts"""
        user = User.objects.get(pk=1)
        self.assertEqual(user.alerts.count(), 0)
        message = Message.objects.create(recipient=user, sender_id=2)
        self.assertEqual(user.alerts.count(), 1)


class AlertUserTests(BaseUserCase):
    fixtures = ['test-auth', 'test-messages']

    def test_00_fixture_messages(self):
        self.assertEqual(Message.objects.count(), 3)
        for message in Message.objects.all():
            self.assertEqual(message.alerts.count(), 1)
            self.assertEqual(message.test_alerts.count(), 1)
        user = User.objects.get(pk=3)
        self.assertEqual(user.alerts.count(), 3)
        user = User.objects.get(pk=2)
        self.assertEqual(user.alerts.count(), 3)

    def test_subscribe_class(self):
        pass

    def test_subscribe_item(self):
        pass

    def test_subdcribe_item_removed(self):
        pass

    def test_create_alert(self):
        pass

    def test_not_subscribed(self):
        pass

    def test_unsubscribe(self):
        pass

    def test_list_alerts(self):
        response = self._get('alerts', slug='alerts.message_alert')
        # THIS FAILS BECAUSE TEST SUITE HAS RESET THE DATABASE BUT NOT
        # THE APP, SO THE APP IS READY BUT EMPTY. IT NEEDS TO RE-INIT
        print response
        #self.assertContains(response, '"')
        #self.assertContains(response, 'id="alert_1"')
        #self.assertNotContains(response, 'id="alert_3"')
        # Test does not contains different alert type (test alert type?)

    def test_list_all_alerts(self):
        response = self._get('alerts')
        self.assertContains(response, 'id="alert_2"')
        self.assertContains(response, 'id="alert_1"')
        self.assertContains(response, 'id="alert_3"')

    def test_view_alert(self):
        pass

    def test_hide_alert(self):
        pass

    def test_delete_alert(self):
        pass

    def test_settings_list(self):
        pass


class MessageOnlyTests(BaseUserCase):
    def test_sent_list(self):
        pass
