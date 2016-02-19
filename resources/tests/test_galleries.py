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
Test Resource Items and Lists
"""

import os

from urllib import urlencode

from .base import BaseCase, BaseUserCase

from django.core.urlresolvers import reverse
from django.core.management import call_command

from resources.models import Resource, ResourceFile, Gallery, Category
from resources.views import GalleryList
from resources.forms import GalleryForm

from person.models import User

class GalleryUserTests(BaseUserCase):
    """Gallery viewing and sorting tests"""
    def test_view_global_gallery(self):
        """Look at the gallery containing every public resource from everyone"""
        resources = ResourceFile.objects.filter(published=True).order_by('-liked')
        self.assertGreater(resources.count(), 3,
                           "Create a few public resources for the global gallery")
        
        response = self._get('resources')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), resources.count())
        # make sure we see uploads from different people
        self.assertGreater(len(set([item.user for item in response.context['object_list']])), 1)
        # make sure every resource is displayed with either the correct licence 
        # or an edit link, when it's ours
        pos = 0
        for resource in resources:
            if resource.user != self.user:
                search_term = resource.license.value
            else:
                search_term = reverse('edit_resource', kwargs={'pk': resource.pk})
            new_pos = response.content.find(str(search_term), pos)
            self.assertGreater(new_pos, -1)
            pos = new_pos
                
        #and we can't upload here directly
        self.assertNotContains(response, '<form method="POST" action="' + reverse('new_gallery'))
    
    def test_narrow_global_gallery(self):
        """make sure we can choose to see only the resources 
        we want to see in the global gallery"""
        resources = ResourceFile.objects.filter(published=True)
        self.assertGreater(resources.count(), 3,
                           "Create a few public resources for the global gallery")
        
        categories = Category.objects.filter(id__in=resources.values('category_id'))
        self.assertGreater(categories.count(), 2,
                           "Create a few categories for the global gallery, and assign public resources to them")
        
        for category in categories:
            items = resources.filter(category=category.pk)
            
            response = self._get('resources', category=category.value)
            self.assertEqual(response.status_code, 200, 
                             'Could not find page for category %s' % category.value)
            self.assertEqual(response.context['object_list'].count(), 
                             items.count(), 'The number of items in category %s is not correct' % category.value)
            for item in items:
                self.assertIn(item, response.context['object_list'])
                self.assertContains(response, item.name)
                
    def test_sort_global_gallery(self):
        "test if ordering for global galleries works as expected"
        resources = ResourceFile.objects.filter(published=True)
        self.assertGreater(resources.count(), 3,
                           "Create a few public resources for the global gallery")
        
        baseresponse = self._get('resources')
        orderlist = [ordering[0] for ordering in GalleryList.orders]
        self.assertGreater(len(orderlist), 3,
                           "Create some possible orderings for your gallery")
        rev_orderlist = [o[1:] if o[0]=='-' else '-' + o for o in orderlist]
        
        #the generator nature of 'orders' in template context doesn't allow us 
        #to use that for testing because it's already 'exhausted'
        
        #make sure the links to the reverse standard order are in the html
        for rev_order in rev_orderlist:
            self.assertContains(baseresponse, rev_order)
            
        #test normal and reverse order
        for order in orderlist + rev_orderlist:
            ordered = resources.order_by(order)
            response = self.client.get(reverse('resources') + '?order=' + order)
            self.assertEqual(response.status_code, 200)
            #conveniently respects ordering when checking for equality
            self.assertEqual(list(response.context['object_list']), list(ordered))
            
            #objects in html in correct order of appearance?
            for i in range(1, len(ordered)):
                first_name = ordered[i-1].name
                second_name = ordered[i].name
                self.assertGreater(response.content.find(str(second_name)),
                                  response.content.find(str(first_name)))
      
    def test_view_user_gallery_owner(self):
        """Look at all my own uploads"""
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 1,
                           "Create another resource for user %s" % self.user)
        
        response = self._get('resources', username=self.user.username)
        self.assertEqual(response.status_code, 200)
        for resource in resources:
            self.assertContains(response, resource.name)
        self.assertContains(response, self.user.username)
        self.assertEqual(response.context['object_list'].count(), resources.count())
        self.assertContains(response, '<form method="POST" action="' + reverse('new_gallery'))
        
    def test_view_user_gallery_not_owner(self):
        """Look at all uploads by another user"""
        owner = User.objects.get(pk=2)
        resources = ResourceFile.objects.filter(user=owner, published=True)
        self.assertGreater(resources.count(), 1,
                           "Create another public resource for user %s" % owner)
        
        response = self._get('resources', username=owner.username)
        self.assertEqual(response.status_code, 200)
        for resource in resources:
            self.assertContains(response, resource.name)
        self.assertContains(response, owner.username)
        self.assertEqual(response.context['object_list'].count(), resources.count())
        self.assertNotContains(response, '<form method="POST" action="' + reverse('new_gallery'))
    
    def test_view_group_gallery(self):
        """Look at a global gallery belonging to a group of users (team in UI), 
        containing all items that have been uploaded into its subgalleries
        not being a member of that group. After this, look at a subgallery, to 
        see if it contains the right items, too."""
        galleries = Gallery.objects.exclude(group=None).exclude(group__in=self.user.groups.all())\
                                   .exclude(user=self.user)
        self.assertGreater(galleries.count(), 1,
                           "Create a group gallery where %s is not a member, and not the owner" % self.user)
        subgallery = galleries[0]
        other_subgallery = galleries[1]
        
        this_group = subgallery.group
        
        #add resources to both subgalleries
        resource_owner = subgallery.group.user_set.all()[0]
        resources = ResourceFile.objects.filter(user=resource_owner, published=True)
        self.assertGreater(resources.count(), 2,
                           "Add a public resource for user %s" % resource_owner)
        subgallery.items.add(resources[0], resources[1])
        other_subgallery.items.add(resources[2])
        
        all_this_groups_items = [item for gal in this_group.galleries.all() for item in gal.items.all()]
        
        # First part: fetch global team gallery page, containing all subgalleries and all their resources
        response = self._get('resources', team=subgallery.group.team.slug)
        
        self.assertEqual(response.status_code, 200)
        
        # make sure all resources from all subgalleries are on that page
        self.assertEqual(len(all_this_groups_items), response.context['object_list'].count())
        for item in subgallery.items.all():
            self.assertContains(response, item.name)
            
        # Second part: fetch a team's subgallery and check if it contains the right resources
        response = self._get('resources', galleries=subgallery.slug, team=subgallery.group.team.slug)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(subgallery.items.count(), response.context['object_list'].count())
        for item in subgallery.items.all():
            self.assertContains(response, item.name)
    
    def test_narrow_user_gallery_owner(self):
        """make sure we can choose to see only the resources 
        we want to see in our own gallery"""
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 2,
                           "Create a few resources for user %s" % self.user)
        
        categories = Category.objects.filter(id__in=resources.values('category_id'))
        self.assertGreater(categories.count(), 2,
                           "Create a few categories for the global gallery, and assign public resources to them")
        
        for category in categories:
            items = resources.filter(category=category.pk)
            
            response = self._get('resources', username=self.user.username, category=category.value)
            self.assertEqual(response.status_code, 200, 
                             'Could not find page for category %s' % category.value)
            self.assertEqual(response.context['object_list'].count(), 
                             items.count(), 'The number of items in category %s is not correct' % category.value)
            for item in items:
                self.assertIn(item, response.context['object_list'])
                self.assertContains(response, item.name)
    
    def test_narrow_user_gallery_not_owner(self):
        """make sure we choose a category in a stranger's gallery"""
        owner = User.objects.get(pk=2)
        resources = ResourceFile.objects.filter(user=owner, published=True)
        self.assertGreater(resources.count(), 2,
                           "Create a few resources for user %s" % owner)
        
        categories = Category.objects.filter(id__in=resources.values('category_id'))
        self.assertGreater(categories.count(), 2,
                           "Create more different categories for public resources by user %s " % owner )
        
        for category in categories:
            items = resources.filter(category=category.pk)
            
            response = self._get('resources', username=owner.username, category=category.value)
            self.assertEqual(response.status_code, 200, 
                             'Could not find page for category %s' % category.value)
            self.assertEqual(response.context['object_list'].count(), 
                             items.count(), 'The number of items in category %s is not correct' % category.value)
            for item in items:
                self.assertIn(item, response.context['object_list'])
                self.assertContains(response, item.name)
    
    # Gallery Search tests
    def test_global_gallery_search(self):
        """Tests the search functionality in galleries"""
        get_param = urlencode({ 'q': '+description searchterm2 searchterm1 -Eight'})

        resources = ResourceFile.objects.filter(published=True).exclude(desc__contains='Eight')\
                                    .filter(desc__contains='description').order_by('-liked')
        self.assertGreater(resources.count(), 0,
                           "Create a public resource which complies to the search query")
        response = self._get('resources', get_param=get_param)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            [int(a.pk) for a in response.context['object_list']],
            [b.pk for b in resources])

        searchterms = [resource.name for resource in resources]

        for term in searchterms:
            self.assertContains(response, ">%s<" % term, 1)

        # The name raw appears in urls, so we look for a tagged name instead
        self.assertNotContains(response, '>Item Eight<')
      
    def test_user_gallery_search(self):
        """Test that we can search for a user's items in that user's global gallery"""
        owner = User.objects.get(pk=2)
        resources = ResourceFile.objects.filter(user=owner, published=True).exclude(name__contains="Four")\
                                    .filter(name__contains="Seven").order_by('-liked')
        self.assertGreater(resources.count(), 0,
                           "Create a public resource which complies to the search query for user %s" % owner)
    
        get_param = urlencode({ 'q': 'Seven -Four'})
        response = self._get('resources', username=owner.username, get_param=get_param)
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(
            [int(a.pk) for a in response.context['object_list']],
            [b.pk for b in resources])

        searchterms = [resource.name for resource in resources]

        for term in searchterms:
            self.assertContains(response, ">%s<" % term, 1)

        # The name raw appears in urls, so we look for a tagged name instead
        self.assertNotContains(response, '>Resource Four<')
      
    def test_specific_gallery_search(self):
        """Test that we can search items in a specific gallery (not global or all items for user)"""
        # prepare gallery
        owner = User.objects.get(pk=2)
        galleries = Gallery.objects.filter(user=owner, group=None)
        self.assertGreater(galleries.count(), 0, "Create a gallery for user %s" % owner)
        gallery = galleries[0]
        
        # add resources which belongs to user 2 to the gallery
        item_search = ResourceFile.objects.get(pk=7)
        item_exclude = ResourceFile.objects.get(pk=4)
        gallery.items.add(item_search, item_exclude)

        # either this, or more fixtures that interfere with already existing tests...
        call_command('rebuild_index', interactive=False, verbosity=0)

        get_param = urlencode({ 'q': 'Seven -Four'})
        response = self._get('resources', username=owner.username, galleries=gallery.slug, get_param=get_param)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.context['object_list'][0].pk), item_search.pk)
        self.assertContains(response, ">%s<" % item_search.name, 1)

        # The name raw appears in urls, so we look for a tagged name instead
        self.assertNotContains(response, '>%s<' % item_exclude.name)
      
    # Gallery Move and Copy resources tests
    def test_move_item_to_gallery(self):
        """Make sure an item can be moved from one gallery to another by its owner,
        make sure template works correctly"""
        # prepare gallery
        galleries = self.user.galleries.all()
        self.assertGreater(galleries.count(), 1)
        src_gallery = galleries[0]
        target_gallery = galleries[1]
        
        # add a resource which belongs to us to the gallery
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)

        # GET
        response = self._get('resource.move', pk=resource.pk, source=src_gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resource.name)
        # this distinguishes move from copy language-independently
        self.assertContains(response, str(src_gallery) + '</td>')

        # move that resource to another gallery
        response = self._post('resource.move', pk=resource.pk, source=src_gallery.pk, data=dict(
            target=target_gallery.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 0)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.all()[0], resource)
    
    def test_move_item_to_gallery_not_gal_owner(self):
        """Make sure that we cannot move items from our own gallery 
        into a gallery which isn't ours, and not a gallery for a group we're in"""
        # prepare galleries
        my_galleries = self.user.galleries.filter(group=None)
        self.assertGreater(my_galleries.count(), 0)
        other_galleries = Gallery.objects.exclude(group__in=self.user.groups.all()).exclude(user=self.user)
        self.assertGreater(other_galleries.count(), 0)

        src_gallery = my_galleries[0]
        target_gallery = other_galleries[0]
        
        # get a resource which belongs to us
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)
        
        # GET
        response = self._get('resource.move', pk=resource.pk, source=src_gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resource.name)
        
        # move that resource to a stranger's gallery
        response = self._post('resource.move', pk=resource.pk, source=src_gallery.pk, data=dict(
            target=target_gallery.pk))
        self.assertEqual(response.status_code, 403, "User shouldn't be able to move an item into another user's gallery")
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 0)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.all()[0], resource)
      
    def test_move_item_to_group_gallery_member(self):
        """Make sure that we can move items into a group gallery 
        if we are a member (not owner) of the group"""
        
        # prepare gallery
        my_galleries = self.user.galleries.filter(group=None)
        self.assertGreater(my_galleries.count(), 0)
        member_galleries = Gallery.objects.exclude(user=self.user).filter(group__in=self.user.groups.all())
        self.assertGreater(member_galleries.count(), 0)
        src_gallery = my_galleries[0]
        target_gallery = member_galleries[0]
        
        # add a resource which belongs to us to the gallery
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)

        # GET
        response = self._get('resource.move', pk=resource.pk, source=src_gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resource.name)

        # move that resource to another gallery
        response = self._post('resource.move', pk=resource.pk, source=src_gallery.pk, data=dict(
            target=target_gallery.pk))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 0)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.all()[0], resource)
    
    def test_move_item_from_group_gallery_member(self):
        """Make sure that we can move our own items out of a group gallery 
        if we are a member (not owner) of the group, but not other people's items"""
        # prepare gallery
        member_galleries = Gallery.objects.exclude(user=self.user).filter(group__in=self.user.groups.all())
        self.assertGreater(member_galleries.count(), 0)
        my_galleries = self.user.galleries.filter(group=None)
        self.assertGreater(my_galleries.count(), 0)
        target_gallery = my_galleries[0]
        src_gallery = member_galleries[0]
        
        # add a resource which belongs to us to the gallery
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)

        # GET
        response = self._get('resource.move', pk=resource.pk, source=src_gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resource.name)

        # move that resource to another gallery
        response = self._post('resource.move', pk=resource.pk, source=src_gallery.pk, data=dict(
            target=target_gallery.pk))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 0)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.all()[0], resource)
        
        # add a resource which does *not* belong to us to the group gallery
        resources = ResourceFile.objects.filter(user=src_gallery.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)

        # try to move that resource to a gallery that is mine
        response = self._post('resource.move', pk=resource.pk, source=src_gallery.pk, data=dict(
            target=target_gallery.pk))
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 1)
        self.assertNotIn(resource, Gallery.objects.get(pk=target_gallery.pk).items.all())

    def test_move_strangers_item_from_group_gallery(self):
        """Make sure group members can move items out of group galleries"""
        # TODO: which target gallery could that be? 
        # I can't move it to my own gallery (forbidden, because it's not my resource), 
        # I can't move it to another user's gallery (forbidden, because it's not my gallery),
        # We can only check if moving it to another gallery belonging to the same group works,
        # and later that moving it to a gallery of another group doesn't
        # We really need a real 'delete' for this, despite the 'move' being funky...
        
        # prepare galleries
        member_galleries = Gallery.objects.exclude(user=self.user).filter(group__in=self.user.groups.all())
        self.assertGreater(member_galleries.count(), 1, 
                           "Create a group gallery that matches the requirements for this test")
        src_gallery = member_galleries[0]
        
        # another gallery for the same group
        target_galleries = member_galleries.filter(group=src_gallery.group).\
          exclude(pk=src_gallery.pk)
        self.assertGreater(target_galleries.count(), 0,
                           "Create another gallery that belongs to group %s" % src_gallery.group)
        target_gallery = target_galleries[0]

        # add a resource which does *not* belong to us, but to someone 
        # totally unrelated (e.g. a member that left the group), 
        # to the source gallery, 
        unrelated_user = User.objects.exclude(groups=src_gallery.group)
        resources = ResourceFile.objects.filter(user=unrelated_user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)
        
        # GET
        response = self._get('resource.move', pk=resource.pk, source=src_gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resource.name)
        # this distinguishes move from copy language-independently
        self.assertContains(response, str(src_gallery) + '</td>')
        
        # try to move that stranger's resource to another gallery belonging to the same group
        response = self._post('resource.move', pk=resource.pk, source=src_gallery.pk, data=dict(
            target=target_gallery.pk))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 0)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 1)
        self.assertIn(resource, Gallery.objects.get(pk=target_gallery.pk).items.all())
        
        # second half: try to move that stranger's resource to another gallery 
        # belonging to another group
        src_gallery.items.add(resource)
        target_galleries = Gallery.objects.exclude(group=src_gallery.group)
        self.assertGreater(target_galleries, 0, 
                           "Create a group gallery that does not belong to group %s" % src_gallery.group)
        target_gallery = target_galleries[0]
        
        # GET - We allow moveing items out of the gallery and between galleries
        # so the GET page will work.
        response = self._get('resource.move', pk=resource.pk, source=src_gallery.pk)
        self.assertEqual(response.status_code, 200)
        
        # try to move a stranger's resource from a gallery belonging to a group I am in 
        # to a gallery of a group I am not in
        response = self._post('resource.move', pk=resource.pk, source=src_gallery.pk, data=dict(
            target=target_gallery.pk))
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 0)

    def test_move_item_to_gallery_not_item_owner(self):
        """Make sure that we cannot move items around that don't belong to us 
        (from stranger's gallery to our own)"""
        # prepare gallery
        other_galleries = Gallery.objects.exclude(group__in=self.user.groups.all()).exclude(user=self.user)
        self.assertGreater(other_galleries.count(), 0)
        member_galleries = Gallery.objects.exclude(user=self.user).filter(group__in=self.user.groups.all())
        self.assertGreater(member_galleries.count(), 0)
        src_gallery = other_galleries[0]
        target_gallery = member_galleries[0]
        
        # add a resource which belongs to someone else to that person's gallery
        resources = ResourceFile.objects.filter(user=src_gallery.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)

        # GET
        response = self._get('resource.move', pk=resource.pk, source=src_gallery.pk)
        self.assertEqual(response.status_code, 403)

        # move that resource to another gallery
        response = self._post('resource.move', pk=resource.pk, source=src_gallery.pk, data=dict(
            target=target_gallery.pk))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 0)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.all()[0], resource)
    
    def test_move_item_from_non_existent_gallery(self):
        """ensure we get a 404 if we try to move an item out of a gallery
        which does not exist"""
        # prepare gallery
        my_galleries = Gallery.objects.filter(user=self.user).exclude(group__in=self.user.groups.all())
        self.assertGreater(my_galleries.count(), 0)
        target_gallery = my_galleries[0]
        
        # prepare my resource
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]

        # GET
        response = self._get('resource.move', pk=resource.pk, source=0)
        self.assertEqual(response.status_code, 404)

        # try to move the resource from nonexistant gallery to my gallery
        response = self._post('resource.move', pk=resource.pk, source=0, data=dict(
            target=target_gallery.pk))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 0)
    
    def test_copy_item_to_gallery(self):
        """Make sure an item can be copied from one gallery to another by its owner, 
        also when the item isn't in any gallery, make sure template works correctly"""
        # prepare galleries
        galleries = self.user.galleries.all()
        self.assertGreater(galleries.count(), 1)
        src_gallery = galleries[0]
        target_gallery = galleries[1]
        
        # add a resource which belongs to us to a gallery
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)
      
        # GET
        response = self._get('resource.copy', pk=resource.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resource.name)
        # this distinguishes move from copy language-independently
        self.assertNotContains(response, src_gallery.name + '</td>')

        # copy that resource to another gallery
        response = self._post('resource.copy', pk=resource.pk, data=dict(target=target_gallery.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.all()[0], resource)
        
        # test the same for a resource that isn't in any gallery
        resource = resources[1]
        response = self._post('resource.copy', pk=resource.pk, data=dict(target=target_gallery.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 2)
        self.assertIn(resource.pk, [gal.pk for gal in Gallery.objects.get(pk=target_gallery.pk).items.all()], )
        
    def test_copy_item_to_gallery_not_gal_owner(self):
        """Make sure that we cannot copy items into a gallery which isn't ours, 
        and not a gallery for a group we're in"""
        # prepare galleries
        my_galleries = self.user.galleries.all()
        self.assertGreater(my_galleries.count(), 0)
        other_galleries = Gallery.objects.exclude(user=self.user).exclude(group__in=self.user.groups.all())
        self.assertGreater(other_galleries.count(), 0)
        src_gallery = my_galleries[0]
        target_gallery = other_galleries[0]
        
        # add a resource which belongs to us to a gallery
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        src_gallery.items.add(resource)
        
        # GET, returns a dropdown box on a page
        response = self._get('resource.copy', pk=resource.pk)
        self.assertEqual(response.status_code, 200)
        
        # copy that resource to another gallery
        response = self._post('resource.copy', pk=resource.pk, data=dict(target=target_gallery.pk))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 0)
        self.assertEqual(Gallery.objects.get(pk=src_gallery.pk).items.count(), 1)
      
    def test_copy_item_to_group_gallery_member(self):
        """Make sure that we can copy own items into a group gallery 
        if we are a member (not owner) of the group"""
        """Make sure an item can be copied from one gallery to another by its owner"""
        # prepare galleries
        galleries = Gallery.objects.exclude(user=self.user).filter(group__in=self.user.groups.all())
        self.assertGreater(galleries.count(), 0)
        target_gallery = galleries[0]
        
        # select a resource
        resources = ResourceFile.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        
        # GET
        response = self._get('resource.copy', pk=resource.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resource.name)

        # copy resource to a gallery
        response = self._post('resource.copy', pk=resource.pk, data=dict(target=target_gallery.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 1)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.all()[0], resource)
      
    def test_copy_item_to_gallery_not_item_owner(self):
        """Make sure we cannot copy items that do not belong to us"""
        # prepare galleries
        galleries = Gallery.objects.filter(user=self.user)
        self.assertGreater(galleries.count(), 1)
        target_gallery = galleries[0]
        
        # select a stranger's resource
        resources = ResourceFile.objects.exclude(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        
        # GET
        response = self._get('resource.copy', pk=resource.pk)
        self.assertEqual(response.status_code, 403)

        # copy resource to a gallery
        response = self._post('resource.copy', pk=resource.pk, data=dict(target=target_gallery.pk))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=target_gallery.pk).items.count(), 0)
    
    # Gallery Edit tests
    def test_edit_my_gallery(self):
        """Make sure that we can change the name of our own gallery"""
        galleries = self.user.galleries.filter(group=None)
        self.assertGreater(galleries.count(), 0)
        gallery = galleries[0]
        oldname = gallery.name
        
        # check GET
        response = self._get('gallery.edit', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], GalleryForm)
        self.assertContains(response, gallery.name)

        # check POST
        response = self._post('gallery.edit', gallery_id=gallery.pk, data={"name": "New Name", "group": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Name")
        self.assertEqual(Gallery.objects.get(pk=gallery.pk).name, "New Name")
        self.assertEqual(Gallery.objects.filter(name=oldname).count(), 0)

    def test_edit_group_gallery_member_fail(self):
        """Make sure that people who do not own a team gallery, but who are members of that gallery's team, cannot change the name/team for that gallery"""
        not_owned_galleries = Gallery.objects.filter(group__in=self.user.groups.all())\
                                           .exclude(user=self.user)
                                         
        self.assertGreater(not_owned_galleries.count(), 0)
        not_owned_gallery = not_owned_galleries[0]
        oldname = not_owned_gallery.name
        
        # check GET
        response = self._get('gallery.edit', gallery_id=not_owned_gallery.pk)
        self.assertEqual(response.status_code, 403)

        # check POST
        response = self._post('gallery.edit', gallery_id=not_owned_gallery.pk, data={"name": "New Name", "group": ""})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=not_owned_gallery.pk).name, oldname)
        
    def test_edit_group_gallery_owner(self):
        """Make sure that group owners can change the name/team of their group 
        gallery"""
        galleries = Gallery.objects.filter(group__in=self.user.groups.all()).filter(user=self.user)
        self.assertGreater(galleries.count(), 0)
        gallery = galleries[0]
        oldname = gallery.name
        
        # check GET
        response = self._get('gallery.edit', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], GalleryForm)
        self.assertContains(response, gallery.name)

        # check POST
        response = self._post('gallery.edit', gallery_id=gallery.pk, data={"name": "New Name", "group": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New Name")
        self.assertEqual(Gallery.objects.get(pk=gallery.pk).name, "New Name")
        self.assertEqual(Gallery.objects.filter(name=oldname).count(), 0)
      
    def test_edit_unrelated_gallery(self):
        """Make sure that everyone unrelated to a 
        gallery cannot edit it"""
        galleries = Gallery.objects.exclude(group=None).exclude(group__in=self.user.groups.all())\
                                                       .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0)
        gallery = galleries[0]
        oldname = gallery.name
        
        # check GET
        response = self._get('gallery.edit', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 403)

        # check POST
        response = self._post('gallery.edit', gallery_id=gallery.pk, data={"name": "New Name", "group": ""})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk).name, oldname)
    
    # Gallery deletion tests
    def test_gallery_deletion_own_gallery(self):
        """Test if galleries can be deleted by owner"""
        galleries = Gallery.objects.filter(user=self.user)
        self.assertGreater(galleries.count(), 0, 
                           "Create a gallery which belongs to user %s" % self.user)
        gallery = galleries[0]
        
        # check GET
        response = self._get('gallery.delete', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, gallery.name)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)
        
        # check POST
        response = self._post('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Gallery.DoesNotExist):
            Gallery.objects.get(pk=gallery.pk)

    def test_gallery_deletion_group_gallery(self):
        """Make sure galleries can be deleted by group member"""
        galleries = Gallery.objects.filter(group__in=self.user.groups.all())\
                                                      .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0, 
            "Create a gallery for a group in which %s is a member, not the owner" % self.user)
        gallery = galleries[0]

        # check GET
        response = self._get('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, gallery.name)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

        # check POST
        response = self._post('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Gallery.DoesNotExist):
            Gallery.objects.get(pk=gallery.pk)
      
    def test_gallery_deletion_group_gallery_non_member(self):
        """Make sure galleries can't be deleted by someone unrelated to the gallery"""
        galleries = Gallery.objects.exclude(group__in=self.user.groups.all())\
                                                      .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0, 
            "Create a group gallery where user %s is neither a group member nor the owner" % self.user)
        gallery = galleries[0]

        # check GET
        response = self._get('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

        # check POST
        response = self._post('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

    # Gallery RSS tests
    def test_gallery_rss_feed(self):
        """Make sure that the main gallery has the correct rss feed, also for
        categories, ordering, subgalleries"""
        galleries = Gallery.objects.all()
        
        resources = ResourceFile.objects.filter(published=True)
        self.assertGreater(resources.count(), 3, "Create some published resources!")
        response = self._get('resources_rss')
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", resources.count())
        for resource in resources:
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())

        # select a category
        cat = resources[0].category
        cat_resources = ResourceFile.objects.filter(published=True, category=cat)
        response = self._get('resources_rss', category=cat.value)
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", cat_resources.count())
        for resource in cat_resources:
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())
        
        # select a username, which is used for all the rest of test
        resources = ResourceFile.objects.exclude(user=self.user) # prevent hassle with unpublished items visible to owner
        u = resources[0].user
        user_resources = resources.filter(user=u)
        response = self._get('resources_rss', username=u.username)
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", user_resources.count())
        for resource in user_resources:
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())
            
        # select a user + a category
        cat = user_resources[0].category
        u_c_resources = user_resources.filter(category=cat)
        response = self._get('resources_rss', username=u.username, category=cat.value)
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", u_c_resources.count())
        for resource in u_c_resources:
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())
            
        # select a user + a gallery    
        user_galleries = u.galleries.all()
        self.assertGreater(user_galleries.count(), 0, "Create a gallery for user %s" % u.username)
        g = user_galleries[0]
        # add a resource to that gallery, so we have some contents
        g.items.add(user_resources[0])
        response = self._get('resources_rss', username=u.username, galleries=g.slug)
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", g.items.count())
        for resource in user_resources.filter(galleries=g):
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())
        
        # select user, gallery and category
        cat = user_resources[0].category
        response = self._get('resources_rss', username=u.username, galleries=g.slug, category=cat.value)
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        expected = user_resources.filter(galleries=g, category=cat)
        self.assertContains(response, "</item>", expected.count())
        for resource in expected:
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())

class GalleryAnonTests(BaseCase):
    """Tests for AnonymousUser"""
    def test_view_all_resources_by_user(self):
        """Look at all uploads from someone, and see only public items"""
        resources = ResourceFile.objects.filter(user=3, published=True)
        self.assertGreater(resources.count(), 0,
                           "Create another resource for user with id 3")
        
        response = self._get('resources', username=User.objects.get(pk=3).username)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resources[0].name)
        self.assertContains(response, User.objects.get(pk=3).username)
        self.assertEqual(response.context['object_list'].count(), resources.count())
   
    def test_gallery_deletion_anon(self):
        """Make sure galleries can't be deleted AnonymousUser"""
        galleries = Gallery.objects.all()
        self.assertGreater(galleries.count(), 0, 
                           "Create a gallery")
        gallery = galleries[0]

        # check GET
        response = self._get('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)
        
        # check POST
        response = self._post('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

