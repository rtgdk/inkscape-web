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

    def setUp(self):
        super(CategoryTests, self).setUp()
        self.count = Resource.objects.count()

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

    def test_category_unacceptable_license(self):
        """Make sure that categories only reject licenses"""
        category = self.getObj(Category, selectable=True, not_acceptable_licenses=self.data['license'])
        self.data['category'] = category.pk
        
        response = self.assertPost('resource.upload', data=self.data, form_errors={
            'license': 'This is not an acceptable license for this category, '
                       'Acceptable licenses:\n * Public Domain (PD)'})
        self.assertEqual(Resource.objects.count(), self.count)

    def test_category_acceptable_license(self):
        """Make sure that categories only accept certain licenses"""
        category = self.getObj(Category, selectable=True, acceptable_licenses=self.data['license'])
        self.data['category'] = category.pk

        response = self.assertPost('resource.upload', data=self.data)
        self.assertEqual(Resource.objects.count(), self.count + 1)

    def test_category_acceptable_type(self):
        category = self.getObj(Category, acceptable_types__isnull=False)
        self.data['category'] = category.pk
        self.data['license'] = 9
        self.data.pop('download')
        self.data.pop('thumbnail')

        response = self.assertPost('resource.upload', data=self.data, form_errors={
            'download': 'Links not allowed in this category: Inkscape Package'})
        self.assertEqual(Resource.objects.count(), self.count)

        self.data['download'] = self.open('preview5.png')
        self.data.pop('link')

        response = self.assertPost('resource.upload', data=self.data, form_errors={
            'download': 'Only image/svg+xml files allowed in Inkscape Package category (found image/png)'})
        self.assertEqual(Resource.objects.count(), self.count)

        self.data['download'] = self.open('file5.svg')
        response = self.assertPost('resource.upload', data=self.data)
        self.assertEqual(Resource.objects.count(), self.count + 1)

    def test_category_acceptable_size(self):
        """Make sure the file size is not too large for the category"""
        category = self.getObj(Category, acceptable_size__isnull=False)

        self.data['category'] = category.pk
        self.data['download'] = self.open('large.png')
        response = self.assertPost('resource.upload', data=self.data, form_errors={
            '_default': None,
            'download': 'Upload is too big for Inkscape Extension category (Max size 1KB)'})
        self.assertEqual(Resource.objects.count(), self.count)

        self.data['download'] = self.open('small.png')
        response = self.assertPost('resource.upload', data=self.data, form_errors={
            '_default': None,
            'download': 'Upload is too small for Inkscape Extension category (Min size 200)'})
        self.assertEqual(Resource.objects.count(), self.count)

        self.data['license'] = 1
        self.data['download'] = self.open('medium.png')
        self.data['thumbnail'] = None
        response = self.assertPost('resource.upload', data=self.data)
        self.assertEqual(Resource.objects.count(), self.count + 1)

    def test_category_acceptable_media_xy(self):
        category = self.getObj(Category, acceptable_media_x__isnull=False)

        self.data['category'] = category.pk
        self.data['thumbnail'] = None
        self.data['license'] = 1

        errors = {'svg': [
          "Image is too small for Inkscape Pallet category (Minimum 20x15)",
          "Image is too large for Inkscape Pallet category (Maximum 25x20)",
               ], 'txt': [
          "Text is too small for Inkscape Pallet category (Minimum 20 Lines, 15 Words)",
          "Text is too large for Inkscape Pallet category (Maximum 25 Lines, 20 Words)",
         ]
        }
        errors['png'] = errors['svg']

        for ext in ('png', 'svg', 'txt'):
            self.data['download'] = self.open('large.' + ext)
            response = self.assertPost('resource.upload', data=self.data, form_errors={'download': errors[ext][1]})

            self.data['download'] = self.open('small.' + ext)
            response = self.assertPost('resource.upload', data=self.data, form_errors={'download': errors[ext][0]})

            self.data['download'] = self.open('medium.' + ext)
            response = self.assertPost('resource.upload', data=self.data)
            self.count += 1
            self.assertEqual(Resource.objects.count(), self.count)

