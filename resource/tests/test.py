#
# Copyright 2015, Maren Hachmann <removemarenhachmannthis@yahoo.com>
#                 Martin Owens <doctormo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Other items in the resource app.
"""
from django.core.urlresolvers import reverse

from resource.models import License, Category, Resource, Tag, Gallery

from .base import BaseCase, BaseAnonCase
from .resources import *
from .gallery import *

class Breadcrumbs(BaseAnonCase):
    def test_breadcrumbs(self):
        """Make sure that breadcrumbs link to the correct parents"""
        #TODO: adapt to actual team page, remove duplicity
        # crumbs for public resources
        resources = Resource.objects.filter(published=True)
        self.assertGreater(resources.count(), 5)
        
        for resource in resources:
            response = self._get('resource', pk=resource.pk)
            searchterms = ("wrapper", 
                           reverse('pages-root'), "Home", 
                           reverse('view_profile', kwargs={'username': resource.user.username}), resource.user,
                           reverse('resources', kwargs={'username': resource.user.username}), "InkSpaces",
                           resource.name)
            pos = 0
            for term in searchterms:
                new_pos = response.content.find(str(term), pos)
                self.assertGreater(new_pos, -1, "Could not find %s" % term)
                pos = new_pos
            
        # crumbs for user-created galleries, no group
        galleries = Gallery.objects.filter(group=None)
        self.assertGreater(galleries, 0,
                           "Please create a gallery that contains a public item and does not belong to a group")
        
        for gallery in galleries:
            response = self._get('resources', galleries=gallery.slug)
                
            searchterms = ("wrapper", 
                           reverse('pages-root'), "Home", 
                           reverse('view_profile', kwargs={'username': resource.user.username}), resource.user,
                           reverse('resources', kwargs={'username': resource.user.username}), "InkSpaces",
                           gallery.name)
            pos = 0
            for term in searchterms:
                new_pos = response.content.find(str(term), pos)
                self.assertGreater(new_pos, -1, "Could not find %s" % term)
                pos = new_pos
        
        # crumbs for user-created galleries, belonging to group
        galleries = Gallery.objects.exclude(group=None)
        self.assertGreater(galleries, 0,
                           "Please create a group gallery that contains a public item")
        
        for gallery in galleries:
            response = self._get('resources', galleries=gallery.slug)
                
            searchterms = ("wrapper", 
                           reverse('pages-root'), "Home", 
                           reverse('team', kwargs={'team': gallery.team.slug}), resource.team,
                           reverse('resources', kwargs={'team': gallery.team.slug}), "InkSpaces",
                           gallery.name)
            pos = 0
            for term in searchterms:
                new_pos = response.content.find(str(term), pos)
                self.assertGreater(new_pos, -1, "Could not find %s" % term)
                pos = new_pos
        
        # crumbs for global gallery
        response = self._get('resources')
        
        searchterms = ("wrapper",
                       reverse('pages-root'), "Home")
        
        pos = 0
        for term in searchterms:
            new_pos = response.content.find(str(term), pos)
            self.assertGreater(new_pos, -1, "Could not find %s" % term)
            pos = new_pos

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
        self.assertEqual(cat.get_absolute_url(), "/en/gallery/4/")

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

