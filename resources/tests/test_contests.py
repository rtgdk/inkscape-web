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
Test all contest related functionality (Gallery and Resource Voting)
"""

__all__ = ('ContestTests',)

import os

from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils.timezone import now

from resources.models import Resource, Gallery, Category, Vote
from person.models import User

from .base import BaseCase

class ContestTests(BaseCase):
    """Test contest related functions"""
    credentials = dict(username='tester', password='123456')
    
    def setUp(self):
        super(ContestTests, self).setUp()
        self.category = self.getObj(Category, name='Artwork')
        self.gallery = Gallery.objects.create(
            user_id=2,
            category=self.category,
            name="Contest Soon",
            slug='contest_soon')
        for item in self.getObj(Resource, galleries__isnull=True,
                not_user=self.user.pk, published=True, count=3):
            self.gallery.items.add(item)
            item.votes.refresh()

    def getContest(self, stage=0, automatic_win=True):
        """Return the gallery in a specific contest 'stage'
        
           -1 - Not a contest
            0 - Not yet started
            1 - Submissions open
            2 - Voting Open
            3 - Contest Counting (null if automatic win)
            4 - Contest Finished
        """
        if stage == -1:
            times = [None] * 4
        else:
            times = [(now() + timedelta(days=1)).date()] * 4
            times += [(now() - timedelta(days=1)).date()] * 4
        self.gallery.contest_submit = times[stage + 3]
        self.gallery.contest_voting = times[stage + 2]
        self.gallery.contest_finish = times[stage + 0]

        if not automatic_win:
            self.gallery.contest_count = times[stage + 1]
        else:
            self.gallery.contest_count = None

        self.gallery.save()
        return self.gallery

    def test_gallery_page(self):
        gallery = self.getContest()
        self.assertEqual(gallery.get_absolute_url(), '/en/gallery/=artwork/contest-soon/')
        get = self.assertGet(gallery, status=200)
        self.assertContains(get, 'Contest')

    def test_statuses(self):
        """Each time status displays correctly on the page"""
        for x, (pend, submit, vote, count, finish) in enumerate([
               (None, None,  None,  None,  None),
               (True,  False, False, False, False),
               (False, True,  False, False, False),
               (False, False, True,  False, False),
               (False, False, False, True,  False),
               (False, False, False, False, True),
              ]):
            gallery = self.getContest(x - 1, automatic_win=False)
            self.assertEqual(gallery.is_contest, x > 0)
            self.assertEqual(gallery.is_pending, pend)
            self.assertEqual(gallery.is_submitting, submit)
            self.assertEqual(gallery.is_voting, vote)
            self.assertEqual(gallery.is_counting, count)
            self.assertEqual(gallery.is_finished, finish)

            gallery = self.getContest(x - 1, automatic_win=True)
            self.assertEqual(gallery.is_contest, x > 0)
            self.assertEqual(gallery.is_pending, pend)
            self.assertEqual(gallery.is_submitting, submit)
            self.assertEqual(gallery.is_voting, vote or count)
            self.assertEqual(gallery.is_counting, None)
            self.assertEqual(gallery.is_finished, finish)

    def test_voting(self):
        """Voting only during voting season and only one per user"""
        before = self.getContest(1)
        for item in self.gallery.items.all():
            url = reverse("resource.like", kwargs={'pk': item.pk, 'like': '+'})
            get = self.assertGet(url)
            self.assertEqual(item.liked, 0)
            self.assertContains(get, 'You may not vote in a contest open for submissions')

        after = self.getContest(2)
        for item in self.gallery.items.all():
            url = reverse("resource.like", kwargs={'pk': item.pk, 'like': '+'})
            get = self.assertGet(url)
            self.assertEqual(get.context_data['object'].liked, 1)
            self.assertContains(get, 'Thank you for your vote')
            self.assertEqual(after.votes.count(), 1)

        for other in self.gallery.items.all():
            if other != item:
                self.assertEqual(other.liked, 0)

    def test_automatic_winner(self):
        """Test that the right winner is selected"""
        after = self.getContest(4, automatic_win=True)
        biggest = None
        for item in self.gallery.items.all():
            item.liked = item.pk * 20
            item.save()
            if not biggest or item.liked > biggest.liked:
                biggest = item
        self.assertEqual(after.winners.count(), 1)
        self.assertEqual(after.winners[0], biggest)
        self.assertEqual(after.winners[0].extra_css, 'ribbon winner')

    def test_manual_winner(self):
        """Test that no winner is selected automatically"""
        after = self.getContest(4, automatic_win=False)
        self.assertEqual(after.winners.count(), 0)

