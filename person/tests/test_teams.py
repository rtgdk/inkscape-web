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
Test team functions
"""

from person.tests.base import BaseUserCase
from person.models import Team, Group

class TeamTests(BaseUserCase):
    def test_01_team_details(self):
        response = self.assertGet('team', team='testteam')
        self.assertContains(response, 'This team is our first test team.')

    def test_10_join_team(self):
        team = Team.objects.get(slug='openteam')
        self.assertNotIn(self.user, team.group.user_set.all())
        response = self.assertGet('team.join', team='openteam')
        self.assertContains(response, "Team membership sucessfully added")
        self.assertIn(self.user, team.group.user_set.all())

    def test_11_watch_team(self):
        team = Team.objects.get(slug='openteam')
        self.assertNotIn(self.user, team.watchers.all())
        response = self.assertGet('team.watch', team='openteam')
        self.assertContains(response, "Now watching this team")
        self.assertIn(self.user, team.watchers.all())

    def test_12_watch_then_join_team(self):
        team = Team.objects.get(slug='openteam')
        response = self.assertGet('team.watch', team='openteam')
        response = self.assertGet('team.join', team='openteam')
        self.assertNotIn(self.user, team.watchers.all())
        self.assertIn(self.user, team.group.user_set.all())



