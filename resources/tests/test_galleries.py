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

from django.utils.timezone import now
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

        response = self.assertGet('resources')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'].count(), resources.count())
        # make sure we see uploads from different people
        self.assertGreater(len(set([item.user for item in response.context['object_list']])), 1)
        # make sure every resource is displayed with either the correct licence
        # or an edit link, when it's ours
        pos = 0

        with open('/tmp/result.txt', 'w') as fhl:
            fhl.write(response.content)

        for resource in resources:
            self.assertTrue(resource.is_available(), "File not available: %s" % resource.download.name)
            self.assertTrue(resource.is_visible(), "File not visible: %s" % resource.download.name)
            if resource.user != self.user:
                search_term = resource.license.value
            else:
                search_term = reverse('edit_resource', kwargs={'pk': resource.pk})
            new_pos = response.content.find(str(search_term), pos)
            self.assertGreater(new_pos, -1, "%s:'%s' not found, does the file exist?" % (unicode(resource), search_term))
            pos = new_pos

        #and we can't upload here directly
        self.assertNotContains(response, '<form method="POST" action="' + reverse('new_gallery'))

    def test_narrow_global_gallery(self):
        """make sure we can choose to see only the resources
        we want to see in the global gallery"""
        resources = ResourceFile.objects.filter(published=True)
        self.assertGreater(resources.count(), 3,
                           "Create a few public resources for the global gallery")

        categories = Category.objects.filter(id__in=resources.values('category_id'), filterable=True)
        self.assertGreater(categories.count(), 2,
                           "Create a few categories for the global gallery, and assign public resources to them")

        for category in categories:
            items = resources.filter(category=category.pk)

            response = self.assertGet('resources', category=category.value)
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

        baseresponse = self.assertGet('resources')
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

        response = self.assertGet('resources', username=self.user.username)
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

        response = self.assertGet('resources', username=owner.username)
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
        response = self.assertGet('resources', team=subgallery.group.team.slug)

        self.assertEqual(response.status_code, 200)

        # make sure all resources from all subgalleries are on that page
        self.assertEqual(len(all_this_groups_items), response.context['object_list'].count())
        for item in subgallery.items.all():
            self.assertContains(response, item.name)

        # Second part: fetch a team's subgallery and check if it contains the right resources
        response = self.assertGet('resources', galleries=subgallery.slug, team=subgallery.group.team.slug)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(subgallery.items.count(), response.context['object_list'].count())
        for item in subgallery.items.all():
            self.assertContains(response, item.name)

    def test_narrow_user_gallery_owner(self):
        """make sure we can choose to see only the resources
        we want to see in our own gallery"""
        resources = ResourceFile.objects.filter(user=self.user, category__filterable=True)
        self.assertGreater(resources.count(), 2,
                           "Create a few resources for user %s" % self.user)

        cat_ids = resources.values_list('category_id', flat=True)
        categories = Category.objects.filter(id__in=cat_ids)
        self.assertGreater(categories.count(), 2,
                "Create a few categories for the global gallery, and assign public resources to them: %s" % str(cat_ids))

        for category in categories:
            items = resources.filter(category=category.pk)

            response = self.assertGet('resources', username=self.user.username, category=category.value)
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

            response = self.assertGet('resources', username=owner.username, category=category.value)
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
        get_param = urlencode({'q': '+description searchterm2 searchterm1 -Eight'})

        resources = ResourceFile.objects.filter(published=True).exclude(desc__contains='Eight')\
                                    .filter(desc__contains='description').order_by('-liked')
        self.assertGreater(resources.count(), 0,
                           "Create a public resource which complies to the search query")
        response = self.assertGet('resources', get_param=get_param)
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

        get_param = urlencode({'q': 'Seven -Four'})
        response = self.assertGet('resources', username=owner.username, get_param=get_param)
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

        get_param = urlencode({'q': 'Seven -Four'})
        response = self.assertGet('resources', username=owner.username, galleries=gallery.slug, get_param=get_param)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.context['object_list'][0].pk), item_search.pk)
        self.assertContains(response, ">%s<" % item_search.name, 1)

        # The name raw appears in urls, so we look for a tagged name instead
        self.assertNotContains(response, '>%s<' % item_exclude.name)

    def assertMoveResource(self, res, src, to, status=200, a=1, b=1, get=200, move='move'):
        """Assert the moving of resources between galleries"""
        kw = dict(pk=res.pk, status=get)
        if src is not None:
            kw['source'] = src and src.pk
        response = self.assertGet('resource.%s' % move, **kw)
        if get == 200:
            self.assertContains(response, res.name)
            # this distinguishes move from copy language-independently
            if move == 'copy':
                self.assertNotContains(response, str(src) + '</td>')
            elif move == 'move':
                self.assertContains(response, str(src) + '</td>')

        kw['status'] = status
        self.assertPost('resource.%s' % move, data={'target': to.pk}, **kw)
        src and self.assertInGallery(res, src, a)
        to and self.assertInGallery(res, to, b)

    def assertCopyResource(self, res, to, status=200, a=1, b=1, get=200):
        """Assert the copying of resources between galleries"""
        return self.assertMoveResource(res, None, to, status, a, b, get, 'copy')

    def assertInGallery(self, resource, gallery, is_in=True):
        """Test a gallery contains the given item (or does not contain)"""
        if isinstance(resource, ResourceFile):
            resource = resource.resource_ptr
        if is_in:
            self.assertIn(resource, gallery.items.all())
        else:
            self.assertNotIn(resource, gallery.items.all())

# ====== Gallery Move and Copy resources tests ====== #

    def test_move_item_to_gallery(self):
        """Make sure an item can be moved from one gallery to another by its
        owner, make sure template works correctly"""
        (src, to) = self.getObj(self.user.galleries.all(), count=2)
        resource = self.getObj(ResourceFile, user=self.user)

        # add a resource which belongs to us to the gallery
        src.items.add(resource)

        # move that resource to another gallery
        self.assertMoveResource(resource, src, to, 200, 0, 1)

    def test_move_item_to_gallery_not_gal_owner(self):
        """Make sure that we cannot move items from our own gallery
        into a gallery which isn't ours, and not a gallery for a group we're in"""
        src = self.getObj(self.user.galleries.filter(group=None))
        to = self.getObj(Gallery.objects.exclude(group__in=self.user.groups.all()).exclude(user=self.user))
        resource = self.getObj(ResourceFile, user=self.user)

        # add a resource which belongs to us to the gallery
        src.items.add(resource)

        # move that resource to a stranger's gallery
        self.assertMoveResource(resource, src, to, 403, 1, 0)

    def test_move_item_to_group_gallery_member(self):
        """Make sure that we can move items into a group gallery
        if we are a member (not owner) of the group"""
        src = self.getObj(self.user.galleries.all(), group=None)
        to = self.getObj(Gallery, exclude=dict(user=self.user),
                         group__in=self.user.groups.all())
        resource = self.getObj(ResourceFile, user=self.user)

        # add a resource which belongs to us to the team gallery
        src.items.add(resource)

        # move that resource to another gallery
        self.assertMoveResource(resource, src, to, 200, 0, 1)

    def test_move_item_from_group_gallery_member(self):
        """
        Make sure that we can move our own items out of a group gallery if we
        are a member (not owner) of the group, but not other people's items.
        """
        src = self.getObj(Gallery, exclude=dict(user=self.user),
                          group__in=self.user.groups.all())
        to = self.getObj(self.user.galleries, group=None)
        resource = self.getObj(ResourceFile, user=self.user)

        # add a resource which belongs to us to the gallery
        src.items.add(resource)

        # move that resource to another gallery
        self.assertMoveResource(resource, src, to, 200, 0, 1)

        # add a resource which does *not* belong to us to the group gallery
        resource = self.getObj(ResourceFile, user=src.user)
        src.items.add(resource)

        # try to move that resource to a gallery that is mine
        self.assertMoveResource(resource, src, to, 403, 1, 0)

    def test_move_strangers_item_from_group_gallery(self):
        """Make sure group members can move items out of group galleries"""
        # I can't move it to my own gallery (forbidden, because it's not my resource),
        # I can't move it to another user's gallery (forbidden, because it's not my gallery),
        # We can only check if moving it to another gallery belonging to the same group works,
        # and later that moving it to a gallery of another group doesn't
        # We really need a real 'delete' for this, despite the 'move' being funky...
        src = self.getObj(Gallery, exclude=dict(user=self.user),
                          group__in=self.user.groups.all())
        to = self.getObj(Gallery, exclude=dict(user=self.user),
                         group_id=src.group.pk)

        # add a resource which does *not* belong to us, but to someone
        # totally unrelated (e.g. a member that left the group),
        # to the source gallery,
        unrelated_user = self.getObj(User, exclude=dict(groups=src.group))
        resource = self.getObj(unrelated_user.resources.all())

        src.items.add(resource)

        # try to move that stranger's resource to another gallery belonging to the same group
        self.assertMoveResource(resource, src, to, 200, 1, 1)

        # second half: try to move that stranger's resource to another gallery
        # belonging to another group
        src.items.add(resource)
        to = self.getObj(Gallery, exclude=dict(group_id=src.group.pk))

        # try to move a stranger's resource from a gallery belonging to a group I am in
        # to a gallery of a group I am not in
        self.assertMoveResource(resource, src, to, 403, 1, 0)

    def test_move_item_to_gallery_not_item_owner(self):
        """Make sure that we cannot move items around that don't belong to us
        (from stranger's gallery to our own)"""
        src = self.getObj(Gallery.objects.exclude(group__in=self.user.groups.all()).exclude(user=self.user))
        to = self.getObj(Gallery, exclude=dict(user=self.user),
                         group__in=self.user.groups.all())

        # add a resource which belongs to someone else to that person's gallery
        resource = self.getObj(ResourceFile, user=src.user)
        src.items.add(resource)

        # move that resource to another gallery
        self.assertMoveResource(resource, src, to, 403, 1, 0, get=403)

    def test_move_item_from_non_existent_gallery(self):
        """ensure we get a 404 if we try to move an item out of a gallery
        which does not exist"""
        to = self.getObj(Gallery, user=self.user,
                exclude=dict(group__in=self.user.groups.all()))
        resource = self.getObj(ResourceFile, user=self.user)

        # try to move the resource from nonexistant gallery to my gallery
        self.assertMoveResource(resource, 0, to, 404, 0, 0, get=404)

    def test_copy_item_to_gallery(self):
        """Make sure an item can be copied from one gallery to another by its owner,
        also when the item isn't in any gallery, make sure template works correctly"""
        (src, to) = self.getObj(self.user.galleries.all(), count=2)

        # add a resource which belongs to us to a gallery
        resource = self.getObj(self.user.resources.all())
        src.items.add(resource)

        self.assertCopyResource(resource, to, 200, 1, 1)

        # test the same for a resource that isn't in any gallery
        resource = self.getObj(self.user.resources.filter(galleries=None))
        self.assertCopyResource(resource, to, 200, 1, 1)

    def test_copy_item_to_gallery_not_gal_owner(self):
        """Make sure that we cannot copy items into a gallery which isn't ours,
        and not a gallery for a group we're in"""
        src = self.getObj(self.user.galleries.all())
        to = self.getObj(Gallery.objects.exclude(user=self.user).exclude(group__in=self.user.groups.all()))

        # add a resource which belongs to us to a gallery
        resource = self.getObj(self.user.resources.all())
        src.items.add(resource)

        self.assertCopyResource(resource, to, 403, 1, 0)

    def test_copy_item_to_group_gallery_member(self):
        """Make sure that we can copy own items into a group gallery
        if we are a member (not owner) of the group"""
        to = self.getObj(Gallery.objects.exclude(user=self.user).filter(group__in=self.user.groups.all()))
        resource = self.getObj(self.user.resources.all())
        self.assertCopyResource(resource, to, 200, 1, 1)

    def test_copy_item_to_gallery_not_item_owner(self):
        """Make sure we cannot copy items that do not belong to us"""
        to = self.getObj(self.user.galleries.all())
        resource = self.getObj(ResourceFile, exclude=dict(user=self.user))
        self.assertCopyResource(resource, to, 403, 1, 0, get=403)

    # Gallery Edit tests
    def test_edit_my_gallery(self):
        """Make sure that we can change the name of our own gallery"""
        galleries = self.user.galleries.filter(group=None)
        self.assertGreater(galleries.count(), 0)
        gallery = galleries[0]
        oldname = gallery.name

        # check GET
        response = self.assertGet('gallery.edit', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], GalleryForm)
        self.assertContains(response, gallery.name)

        # check POST
        response = self.assertPost('gallery.edit', gallery_id=gallery.pk, data={"name": "New Name", "group": ""})
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
        response = self.assertGet('gallery.edit', gallery_id=not_owned_gallery.pk)
        self.assertEqual(response.status_code, 403)

        # check POST
        response = self.assertPost('gallery.edit', gallery_id=not_owned_gallery.pk, data={"name": "New Name", "group": ""})
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
        response = self.assertGet('gallery.edit', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], GalleryForm)
        self.assertContains(response, gallery.name)

        # check POST
        response = self.assertPost('gallery.edit', gallery_id=gallery.pk, data={"name": "New Name", "group": ""})
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
        response = self.assertGet('gallery.edit', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 403)

        # check POST
        response = self.assertPost('gallery.edit', gallery_id=gallery.pk, data={"name": "New Name", "group": ""})
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
        response = self.assertGet('gallery.delete', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, gallery.name)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

        # check POST
        response = self.assertPost('gallery.delete', gallery_id=gallery.id)
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
        response = self.assertGet('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, gallery.name)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

        # check POST
        response = self.assertPost('gallery.delete', gallery_id=gallery.id)
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
        response = self.assertGet('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

        # check POST
        response = self.assertPost('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

    # Gallery RSS tests
    def test_gallery_rss_feed(self):
        """Make sure that the main gallery has the correct rss feed, also for
        categories, ordering, subgalleries"""
        # RSS Feed only shows things in the last month
        ResourceFile.objects.all().update(created=now())

        categories = Category.objects.filter(filterable=True)
        galleries = Gallery.objects.filter()
        resources = ResourceFile.objects.filter(published=1)

        self.assertGreater(resources.count(), 3, "Create some published resources!")
        response = self.assertGet('resources_rss')
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", resources.count())
        for resource in resources:
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())

        # select a category
        cat = resources.filter(category__in=categories)[0].category
        cat_resources = ResourceFile.objects.filter(published=True, category=cat)
        response = self.assertGet('resources_rss', category=cat.value)
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", cat_resources.count())
        for resource in cat_resources:
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())

        # select a username, which is used for all the rest of test
        resources = ResourceFile.objects.exclude(user=self.user) # prevent hassle with unpublished items visible to owner
        u = resources[0].user
        user_resources = resources.filter(user=u)
        response = self.assertGet('resources_rss', username=u.username)
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", user_resources.count())
        for resource in user_resources:
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())

        # select a user + a category
        cat = user_resources[0].category
        u_c_resources = user_resources.filter(category=cat)
        response = self.assertGet('resources_rss', username=u.username, category=cat.value)
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
        response = self.assertGet('resources_rss', username=u.username, galleries=g.slug)
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        self.assertContains(response, "</item>", g.items.count())
        for resource in user_resources.filter(galleries=g):
            self.assertContains(response, resource.name)
            self.assertContains(response, resource.get_absolute_url())

        # select user, gallery and category
        cat = user_resources[0].category
        response = self.assertGet('resources_rss', username=u.username, galleries=g.slug, category=cat.value)
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

        response = self.assertGet('resources', username=User.objects.get(pk=3).username)
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
        response = self.assertGet('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

        # check POST
        response = self.assertPost('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

