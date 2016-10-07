#
# Copyright 2016, Maren Hachmann <marenhachmann@yahoo.com>
#                 Martin Owens <doctormo@gmail.com>
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
Test Resource Categories
"""

__all__ = ('UploadCategoryTests')

import os

from .base import BaseCase
from resources.models import Resource, Category


class CategoryTests(BaseCase):
    credentials = dict(username='tester', password='123456')

    def assertCategory(self, **kw):
        category = self.getObj(Category, **kw)
        response = self.assertGet(category.get_absolute_url(), status=200)
        for item in response.context['object_list']:
            self.assertEqual(item.category, category)
        return (category, response)

    def test_category_list(self):
        """List a category page"""
        (cat1, res1) = self.assertCategory(filterable=True)
        (cat2, res2) = self.assertCategory(filterable=False)
        self.assertContains(res1, "<label>%s</label>" % str(cat1))
        self.assertContains(res1, "Media Category")
        self.assertNotContains(res2, "<label>%s</label>" % str(cat2))
        self.assertNotContains(res2, "Media Category")


    def test_submit_item_unacceptable_license(self):
        """Make sure that categories only accept certain licenses"""
        # Current setting for Screenshots (only 'all rights reserved') might need to be changed.
        categories = Category.objects.filter(selectable=True)\
            .exclude(acceptable_licenses=self.data['license'])
        # The selected category MUST be visible or django forms will consider
        # the selection to be None (and likely cause errors)
        self.assertGreater(categories.count(), 0,
            "Create a visible category where license id %s isn't acceptable" % self.data['license'])
        self.data['category'] = categories[0].pk

        num = Resource.objects.count()
        
        response = self.assertPost('resource.upload', data=self.data, form_errors={
            'license': 'This is not an acceptable license for this category, '
                       'Acceptable licenses:\n * Public Domain (PD)'})
        self.assertEqual(Resource.objects.count(), num)


