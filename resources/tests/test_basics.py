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

from .base import BaseCase, BaseAnonCase, BaseBreadcrumbCase

class Breadcrumbs(BaseBreadcrumbCase):
    def test_resource_breadcrumbs(self):
        """Resource item breadcrumbs"""
        #TODO: adapt to actual team page, remove duplicity
        # crumbs for public resources
        resources = Resource.objects.filter(published=True)
        self.assertGreater(resources.count(), 5)
        
        for resource in resources:
            self.assertBreadcrumbs(resource,
                (reverse('pages-root'), "Home"),
                (resource.user.get_absolute_url(), str(resource.user)),
                (reverse('resources', kwargs={'username': resource.user.username}), "InkSpaces"),
                (resource.get_absolute_url(), resource.name))

    def test_gallery_breadcrumbs(self):
        """crumbs for user-created galleries, no group"""
        galleries = Gallery.objects.filter(group=None)
        self.assertGreater(galleries, 0,
            "Please create a gallery that contains a public item and does not belong to a group")
        
        for gallery in galleries:
            self.assertBreadcrumbs(gallery,
                (reverse('pages-root'), "Home"),
                (gallery.user.get_absolute_url(), str(gallery.user)),
                (reverse('resources', kwargs={'username': gallery.user.username}), "InkSpaces"),
                (gallery.get_absolute_url(), gallery.name,))

    def test_group_gallery_breadcrumbs(self):
        """crumbs for user-created galleries, belonging to group"""
        galleries = Gallery.objects.exclude(group=None)
        self.assertGreater(galleries, 0,
            "Please create a group gallery that contains a public item")
        
        for gallery in galleries:
            self.assertBreadcrumbs(gallery,
                (reverse('pages-root'), "Home"),
                (gallery.group.get_absolute_url(), gallery.group.team.name),
                (reverse('resources', kwargs={'team': gallery.group.team.slug}), "InkSpaces"),
                (gallery.get_absolute_url(), gallery.name,))

    def test_global_gallery(self):
        """crumbs for global gallery"""
        self.assertBreadcrumbRequest('resources',
                (reverse('pages-root'), "Home"),
        )


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

