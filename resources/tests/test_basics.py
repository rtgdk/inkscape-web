#
# Copyright 2015, Maren Hachmann <marenhachmann@yahoo.com>
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
Other items in the resource app.
"""
from django.core.urlresolvers import reverse

from resources.models import License, Category, Resource, Tag, Gallery

from .base import BaseCase

class LicenseTests(BaseCase):
    def test_license_methods(self):
        """Tests if license methods return expected output"""
        license = License.objects.get(code="PD")
        self.assertEqual(license.value, license.code)
        self.assertEqual(license.is_free(), True)
        self.assertEqual(license.is_all_rights(), False)
        self.assertEqual(str(license), "%s (%s)" % (license.name, license.code))
    
        license = License.objects.get(code="(C)")
        self.assertEqual(license.value, license.code)
        self.assertEqual(license.is_free(), False)
        self.assertEqual(license.is_all_rights(), True)
        self.assertEqual(str(license), "%s (%s)" % (license.name, license.code))

class CategoryTests(BaseCase):
    #These tests are not finished, as design seems to be in flux, but can be fleshed out if required       
    def test_category_methods(self):
        """Test methods for categories""" 
        cat = Category.objects.get(name="UI Mockup")
        self.assertEqual(cat.value, "ui-mockup")
        self.assertEqual(cat.get_absolute_url(), "/en/gallery/=ui-mockup/")

class TagTests(BaseCase):
    def test_tags(self):
        # currently these are not exposed to the user. 
        # Why do they have a 'parent'? Are circles prevented?
        resource = Resource.objects.all()[0]
        self.assertEqual(list(resource.tags.all()), [])
        
        resource.tags.create(name="landscape")
        resource.tags.create(name="moon")
        
        self.assertEqual([tag.name for tag in resource.tags.all().order_by('name')], ["landscape", "moon"])
        self.assertIn(resource, Tag.objects.get(name="landscape").resources.all())
        #self.fail("Expose tags to user (form, view, template) and implement cleanup for tag strings so there is more to test")

