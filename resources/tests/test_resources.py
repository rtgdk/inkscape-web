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

__all__ = ('ResourceTests', 'ResourceAnonTests')

import os

from .base import BaseCase

from django.core.urlresolvers import reverse

from resources.models import Resource, Resource, Quota, Gallery, Category
from resources.forms import ResourceForm, ResourceEditPasteForm, ResourcePasteForm
from resources.utils import video_embed

from person.models import User

class ResourceTests(BaseCase):
    """Test non-request functions and methods"""
    def test_slug(self):
        """Unique slug creation"""
        data = {
          'name': 'Test Resource Title',
          'user': User.objects.get(pk=1),
        }
        one = Resource.objects.create(**data)
        self.assertEqual(one.slug, 'test-resource-title')
        two = Resource.objects.create(**data)
        self.assertEqual(two.slug, 'test-resource-title+0')
        now = Resource.objects.create(**data)
        self.assertEqual(now.slug, 'test-resource-title+1')
        two.delete()
        now = Resource.objects.create(**data)
        self.assertEqual(now.slug, 'test-resource-title+0')

    def test_file_deletion(self):
        """Check that removal of a Resource removes the corresponding Resource and vice versa"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 1,
            "Create resource, so there are at least two")

        resource = resources[0]
        Resource.objects.get(pk=resource.pk).delete()
        with self.assertRaises(Resource.DoesNotExist):
            Resource.objects.get(pk=resource.pk)
            
        resource = resources[0]
        resource.delete()
        with self.assertRaises(Resource.DoesNotExist):
            Resource.objects.get(pk=resource.pk)

    def test_media_size(self):
        """Make sure file sizes are reported"""
        svg = Resource.objects.get(download__contains='file5.svg')
        self.assertTupleEqual(svg.find_media_coords(), (67, 83))

        svg = Resource.objects.get(download__contains='file4.svg')
        self.assertTupleEqual(svg.find_media_coords(), (-1, -1))

    def test_mime_type(self):
        """Make sure file types are right"""
        pdf = Resource.objects.get(media_type__contains='pdf').mime()
        self.assertEquals(pdf.subtype(), 'pdf')
        self.assertEquals(pdf.type(), 'document')
        self.assertEquals(pdf.icon(), '/static/mime/pdf.svg')

        unknown = Resource.objects.get(media_type__contains='/man').mime()
        self.assertEquals(unknown.icon(), '/static/mime/unknown.svg')


class ResourceViewTests(BaseCase):
    credentials = dict(username='tester', password='123456')

    def test_view_my_public_item_detail(self):
        """Testing item detail view and template for public own items,
        and make sure the view counter is correctly incremented"""
        #make sure we own the file and it's public
        resources = Resource.objects.filter(published=True, user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a published resource for user %s" % self.user)
        resource = resources[0]
        num_views = resource.viewed
        
        response = self.assertGet('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        self.assertContains(response, str(self.user))
        # can't increment view number on my own items
        self.assertEqual(response.context['object'].viewed, num_views)
        self.assertEqual(Resource.objects.get(pk=resource.pk).viewed, num_views)
        
    def test_view_my_unpublished_item_detail(self):
        """Testing item detail view and template for non-published own items"""
        # make sure we own the file and it is unpublished
        resources = Resource.objects.filter(published=False, user=self.user, viewed=0)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource for user %s" % self.user)
        resource = resources[0]
        
        response = self.assertGet('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        self.assertContains(response, str(self.user))
        # can't increment view number on my own items
        self.assertEqual(response.context['object'].viewed, resource.viewed)
        self.assertEqual(Resource.objects.get(pk=resource.pk).viewed, 0)
    
    def test_view_someone_elses_public_item_detail(self):
        """Testing item detail view and template for someone elses public resource:
        license, picture, description, username should be contained, and views should
        be counted correctly"""
        # make sure we don't own the file and it is public
        resources = Resource.objects.filter(published=True).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a published resource that doesn't belong to user %s" % self.user)
        resource = resources[0]
        
        response = self.assertGet('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        self.assertContains(response, str(resource.user) )
        self.assertContains(response, resource.license.value)
        self.assertEqual(Resource.objects.get(pk=resource.pk).viewed, 1)
        
        # number of views should only be incremented once per user session
        response = self.assertGet('resource', pk=resource.pk)
        self.assertEqual(Resource.objects.get(pk=resource.pk).viewed, 1)

    def test_view_someone_elses_unpublished_item_detail(self):
        """Testing item detail view for someone elses non-public resource: 
        Page not found and no incrementing of view number"""
        # Make sure we don't own the resource
        resources = Resource.objects.filter(published=False).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which doesn't belong to %s for this test" % self.user)
        resource = resources[0]
        num = resource.viewed
        
        response = self.assertGet('resource', pk=resource.pk, status=404)
        self.assertEqual(Resource.objects.get(pk=resource.pk).viewed, num)
    
    def test_view_text_file_detail(self):
        """Check if the text of a textfile is displayed on item view page and its readmore is not"""
        # specific text file resource, description contains a 'Readmore' marker: [[...]]
        resource = Resource.objects.get(pk=2) 
        self.assertEqual(resource.desc, "Big description for Resource Two[[...]]And Some More",
                        "Someone changed the description text of resource 2, please change back to \"Big description for Resource Two[[...]]And Some More\"")
        response = self.assertGet('resource', pk=resource.pk)
        self.assertContains(response, 'Text File Content')
        self.assertContains(response, 'Big description for Resource Two')
        self.assertContains(response, 'readme.txt')
        self.assertNotContains(response, 'And Some More')
    
    def test_view_public_resource_full_screen(self):
        """Check that a resource can be viewed in full screen, 
        and that fullview number is incremented when a user visits
        a published item in 'full screen glory'"""
        resources = Resource.objects.filter(published=True, fullview=0)
        self.assertGreater(resources.count(), 0,
            "Create a published resource with 0 fullscreen views")
        resource = resources[0]
        
        response = self.assertGet('view_resource', pk=resource.pk, follow=False)
        self.assertEqual(response.url, 'http://testserver' + resource.download.url)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 1)
        
        # The full view counter is untracked so every request will increment the counter
        response = self.assertGet('view_resource', pk=resource.pk)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 2)
        
    def test_view_own_unpublished_resource_full_screen(self):
        """Check that we can look at our unpublished resource in full screen mode,
        and that fullviews aren't counted as long as the resource isn't public"""
        resources = Resource.objects.filter(published=False, user=self.user, fullview=0)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource with 0 fullscreen views for user %s" % self.user)
        resource = resources[0]
        
        response = self.assertGet('view_resource', pk=resource.pk, status=200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 0)

    def test_view_someone_elses_unpublished_resource_full_screen(self):
        """Make sure that fullscreen view for unpublished items 
        doesn't work if they are not ours. Also make sure this 
        doesn't increment the fullview counter"""
        resources = Resource.objects.filter(published=False, fullview=0).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which doesn't belong to user %s and has 0 full screen views" % self.user)
        resource = resources[0]
        
        response = self.assertGet('view_resource', pk=resource.pk, status=404)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 0)
    
    def test_view_readme(self):
        """Download the description as a readme file"""
        resource = Resource.objects.get(pk=2)
        self.assertNotEqual(resource.desc.find("[[...]]"), -1,
                            "Please add a readmore marker ([[...]] back to the description of resource 2")
        response = self.assertGet('resource.readme', pk=resource.pk)
        self.assertContains(response, resource.desc)

    def test_download(self):
        """Download the actual file"""
        resources = Resource.objects.filter(published=True, downed=0)
        self.assertGreater(resources.count(), 0,
                           'Create a public resource with 0 downloads')
        resource = resources[0]
        response = self.assertGet('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False, status=302)

        # We expect a 'dl' link instead of a 'media' link because
        # we hand off the download even in development versions.
        filename = resource.download.url.split('/')[-1]
        self.assertEqual(response.url, 'http://testserver/dl/test/' + filename)

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 1)

        #try again, counter should increment again
        response = self.assertGet('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False)

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 2)
        
    def test_download_non_existent_file(self):
        resources = Resource.objects.filter(published=True, downed=0)
        self.assertGreater(resources.count(), 0,
                           'Create a public resource with 0 downloads')
        resource = resources[0]
        response = self.assertGet('download_resource', pk=resource.pk,
                       fn=resource.filename() + 'I_don_t_exist', follow=True, status=200)

        self.assertContains(response, 'Can not find file &#39;%s&#39;' % (resource.filename() + 'I_don_t_exist'))
        self.assertContains(response, resource.description())

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 0)
        
    def test_download_non_public_file_not_owner(self):
        resources = Resource.objects.filter(published=False).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
                           'Create a non-public resource with 0 downloads which does not belong to %s' % self.user)
        resource = resources[0]
        num_dl = resource.downed
        response = self.assertGet('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False, status=404)

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, num_dl)
        

class UploadViewTests(BaseCase):
    credentials = dict(username='tester', password='123456')

    def test_submit_item(self):
        """Tests views and templates for uploading a new resource file"""
        # This part could be repeated for different inputs/files to check for errors and correct saving, subtests? 
        # Could become a mess if all are in one test.
        num = Resource.objects.count() 
        
        # check GET
        response = self.assertGet('resource.upload')
        self.assertIsInstance(response.context['form'], ResourceForm)
        
        # check POST
        response = self.assertPost('resource.upload', data=self.data, status=200)
        self.assertEqual(Resource.objects.count(), num + 1)

    def test_submit_long_filename(self):
        """Submit an item with an extra large filename"""
        for x in range(92, 97):
            data = self.data
            name = 'x' * x + '.svg'
            data['download'] = self.open('file5.svg', name=name)
            data['thumbnail'] = self.open('preview5.png', name=name)
            res = self.assertPost('resource.upload', data=data, status=200)

            out = res.context_data['object'].download.name
            self.assertLess(len(out), 101)
            self.assertEqual(out[:-12], 'resources/file/' + ('x' * 73))

            out = res.context_data['object'].thumbnail.name
            self.assertLess(len(out), 101)
            self.assertEqual(out[:-12], 'resources/thumb/' + ('x' * 72))

        name = 'x' * 97 + '.svg'
        data['download'] = self.open('file5.svg', name=name)
        data['thumbnail'] = self.open('preview5.png', name=name)
        self.assertPost('resource.upload', data=data, form_errors={
            'download': "Ensure this filename has at most 100 characters (it has 101).",
            'thumbnail': "Ensure this filename has at most 100 characters (it has 101)."
        })

    def test_submit_gallery_item(self):
        """Test if I can upload a file into my own gallery when a gallery is selected"""
        galleries = Gallery.objects.filter(user=self.user)
        self.assertGreater(galleries.count(), 0,
            "Create a gallery for user %s" % self.user)
        gallery = galleries[0]
        num = Resource.objects.count()
        
        (get, post) = self.assertBoth('resource.upload', gallery_id=gallery.pk, data=self.data, status=200)
        self.assertEqual(get.context['gallery'], gallery)
        self.assertIsInstance(get.context['form'], ResourceForm)
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertEqual(post.context['object'].gallery, gallery)

    def test_paste_text_POST(self):
        """Test pasting a text, a long one (success) 
        and a short one (fail)"""
        num = Resource.objects.count()
        data = {'download': "foo" * 100,}
        shortdata = {'download': "blah" * 5}
        
        (get, post) = self.assertBoth('pastebin', data=data, status=200)
        self.assertIsInstance(get.context['form'], ResourcePasteForm)
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertContains(post, "foofoo")
        
        response = self.assertPost('pastebin', data=shortdata, form_errors={
              '_default': None,
              'download': 'Text is too small for the pastebin.',
            })
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertContains(response, "blahblah")

    def test_submit_gallery_failure(self):
        """Test when no permission to submit exists"""
        galleries = Gallery.objects.exclude(user=self.user).exclude(group__in=self.user.groups.all())
        self.assertGreater(galleries.count(), 0,
            "Create a gallery for user other than %s" % self.user)
        gallery = galleries[0]
        num = Resource.objects.count()
        
        # check GET
        response = self.assertGet('resource.upload', gallery_id=gallery.pk, status=403)
        
        # check POST
        response = self.assertPost('resource.upload', gallery_id=gallery.pk, data=self.data, status=403)
        self.assertEqual(Resource.objects.count(), num)

    def test_submit_group_gallery(self):
        """Test to upload a resource when a gallery is group based, 
        and the user is member of the group, but not owner of the gallery"""
        galleries = Gallery.objects.filter(group__in=self.user.groups.all())\
                      .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0,
            "Create a group gallery where user %s is group member, but not gallery owner" % self.user)
        gallery = galleries[0]
        num = Resource.objects.count()

        # check GET
        response = self.assertGet('resource.upload', gallery_id=gallery.pk, status=200)
        self.assertEqual(response.context['gallery'], gallery)
        self.assertIsInstance(response.context['form'], ResourceForm)
        
        # check POST
        response = self.assertPost('resource.upload', gallery_id=gallery.pk,
            data=self.data, status=200)
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertEqual(response.context['object'].gallery, gallery)

    def test_drop_item(self):
        """Drag and drop file (ajax request)"""
        num = Resource.objects.count()
        
        (_, post) = self.assertBoth('resource.drop', status=200, data={
          'name': "New Name", 'download': self.download})
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertContains(post, 'OK|')

    def test_submit_item_quota_exceeded(self):
        """Check that submitting an item which would make the user exceed the quota will fail"""
        default_quota = Quota.objects.filter(group__isnull=True)[0]
        default_quota.size = 1 # 1024 byte
        default_quota.save()
        name = self.download.name
        quot = self.user.quota()

        self.assertGreater(os.path.getsize(name), quot,
            "Make sure that the file %s is bigger than %d byte" % (name, quot))

        response = self.assertPost('resource.upload', data=self.data,
            form_errors={'download': 'Not enough space to upload this file.'})

    def test_publish_item(self):
        """Check that we can publish our own items"""
        resources = Resource.objects.filter(published=False, user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource for user %s" % self.user)
        resource = resources[0]

        # check GET
        # TODO: currently displays the detail page
        response = self.assertGet('publish_resource', pk=resource.pk, status=200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, False)
        
        # check POST
        # TODO: there's no link to this any more in galleries, replaced by 'move' icon
        response = self.assertPost('publish_resource', pk=resource.pk, status=200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, True)
        
        # Make sure nothing weird will happen when published twice.
        response = self.assertPost('publish_resource', pk=resource.pk, status=200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, True)

    def test_publish_another_persons_item(self):
        """Make sure we can't publish resources which are not ours"""
        resource = self.getObj(Resource, published=False, not_user=self.user)
        self.assertBoth('publish_resource', pk=resource.pk, status=403)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, False)

    # Resource Edit tests:
    def test_edit_paste_being_the_owner(self):
        """Test if we can access the paste edit page for our own item"""
        # Make sure we own the file and that it IS a pasted text item
        resource = self.getObj(Resource, user=self.user, category=1)
        
        # check GET
        response = self.assertGet('edit_resource', pk=resource.pk)
        self.assertIsInstance(response.context['form'], ResourceEditPasteForm)
        self.assertContains(response, resource.name)
        
        # check POST
        data = {
            'name': 'New Name',
            'license': 1,
            'media_type': 'text/css',
            'download': 'A' * 300,
        }
        self.assertPost('edit_resource', pk=resource.pk, data=data, status=200)

    def test_edit_item_being_the_owner(self):
        """Test if we can edit an item which belongs to us"""
        # Make sure we own the file and that it's NOT a pasted text item
        resource = self.getObj(Resource, user=self.user, not_category=1)

        (get, _) = self.assertBoth('edit_resource', pk=resource.pk, data={'owner': True})
        self.assertIsInstance(get.context['form'], ResourceForm)
        self.assertContains(get, resource.name)
      
    def test_edit_item_by_other_user(self):
        """Check that we can't access the edit form for other people's items"""
        #make sure we don't own the file
        resources = Resource.objects.exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which doesn't belong to user %s" % self.user)
        resource = resources[0]
        
        # check GET
        response = self.assertGet('edit_resource', pk=resource.pk, status=403)
        
        # check POST
        response = self.assertPost('edit_resource', pk=resource.pk, data=self.data, status=403)
        self.assertNotEqual(resource.description, self.data['desc'])
        
    # Resource Deletion tests:
    def test_delete_own_item(self):
        """Check that we can delete our own items"""
        resources = Resource.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which belongs to user %s" % self.user)
        resource = resources[0]
        
        # check GET
        response = self.assertGet('delete_resource', pk=resource.pk, status=200)
        
        # check POST
        response = self.assertPost('delete_resource', pk=resource.pk, follow=False, status=302)
        
        with self.assertRaises(Resource.DoesNotExist):
            deleted = Resource.objects.get(pk=resource.pk)
        
        deleted = self.assertGet('resource', pk=resource.pk, status=404)
        
    def test_delete_another_persons_item(self):
        """Make sure that we can't delete other people's items"""
        resources = Resource.objects.exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which does not belong to user %s" % self.user)
        resource = resources[0]
        
        self.assertGet('delete_resource', pk=resource.pk, status=403)
        self.assertPost('delete_resource', pk=resource.pk, status=403)
        
        self.assertEqual(resource, Resource.objects.get(pk=resource.pk))

    def test_no_revision_on_create(self):
        """We don't get a revision with a new resource"""
        self.assertPost('resource.drop', data={
          'name': "my_resource",
          'download': self.download,
        }, status=200)
        resource = Resource.objects.get(name='my_resource')
        self.assertEqual(resource.revisions.count(), 0)

    def test_no_revision_on_edit(self):
        """We don't get a revision with a no-file edit"""
        resource = self.getObj(Resource, user=self.user, category=3)
        data = self.data.copy()
        data.pop('download')
        data['name'] = 'updated'
        response = self.assertPost('edit_resource', pk=resource.pk, data=data, status=200)
        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.name, 'updated')
        self.assertEqual(resource.revisions.count(), 0)

    def test_new_revision_on_save(self):
        """We do get a revision with a file edit"""
        resource = self.getObj(Resource, user=self.user, category=3)
        self.assertPost('edit_resource', pk=resource.pk, data=self.data, status=200)
        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.name, 'Test Resource Title')
        self.assertEqual(resource.revisions.count(), 1)


class ResourceVoteTests(BaseCase):
    credentials = dict(username='tester', password='123456')

    def test_like_item_not_being_owner(self):
        """Like a gallery item which belongs to someone else"""
        resources = Resource.objects.exclude(user=self.user).filter(liked=0)
        self.assertGreater(resources.count(), 0,
            "Create a resource which doesn't belong to user %s" % self.user)
        resource = resources[0]

        response = self.assertGet('resource.like', pk=resource.pk, like='+', status=200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).liked, 1)
        
        # try a second time, should not increment
        response = self.assertGet('resource.like', pk=resource.pk, like='+')
        self.assertEqual(Resource.objects.get(pk=resource.pk).liked, 1)

        response = self.assertGet('resource.like', pk=resource.pk, like='-', status=200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).liked, 0)
        
        # and a second time, for good measure, shouldn't change anything
        response = self.assertGet('resource.like', pk=resource.pk, like='-', status=200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).liked, 0)
        
    def test_like_unpublished_item_not_being_owner(self):
        """Like a gallery item which belongs to someone else, and is not public
        - should fail and not change anything in db"""
        resources = Resource.objects.filter(published=False)\
            .exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource with no likes which doesn't belong to user %s" % self.user)

        previous_value = resources[0].liked
        # Make a request to this resource like link
        response = self.assertGet('resource.like', pk=resources[0].pk, like='+', follow=False, status=404)
        # This should not increment the counter
        self.assertEqual(resources[0].liked, previous_value)
        
    def test_like_item_being_owner(self):
        """Like a gallery item which belongs to me should fail"""
        # use the fact that counter would start with 1, if liking would work
        resources = Resource.objects.filter(user=self.user, liked__gt=1)
        self.assertGreater(resources.count(), 0,
            "Create a resource for user %s" % self.user)

        resource = resources[0]
        num_likes = resource.liked

        response = self.assertGet('resource.like', pk=resource.pk, like='+', status=403)
        self.assertEqual(Resource.objects.get(pk=resource.pk).liked, num_likes)


class ResourceAnonTests(BaseCase):
    """Tests for AnonymousUser"""
    
    def test_view_public_item_detail_anon(self):
        """Testing item detail view and template for public items,
        and make sure the view counter is correctly incremented (once per session)"""
        #make sure the file is public
        resources = Resource.objects.filter(published=True)
        self.assertGreater(resources.count(), 0,
            "Create a published resource")
        resource = resources[0]
        num_views = resource.viewed
        
        # the response already contains the updated number
        response = self.assertGet('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        # we don't have any real views saved in the db, so we start with zero

        #self.assertEqual(response.context['object'].viewed, num_views + 1)
        
        # number of views should only be incremented once per user session
        #response = self.assertGet('resource', pk=resource.pk)
        #self.assertEqual(Resource.objects.get(pk=resource.pk).viewed, num_views + 1)
    
    def test_view_public_resource_full_screen_anon(self):
        """Check that an anonymous user can look at a
        resource in full screen, and that fullview number is incremented
        every time"""
        resources = Resource.objects.filter(published=True, fullview=0)
        self.assertGreater(resources.count(), 0,
            "Create a published resource with 0 fullscreen views")
        resource = resources[0]
        
        response = self.assertGet('view_resource', pk=resource.pk, follow=False)
        self.assertEqual(response.url, 'http://testserver' + resource.download.url)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 1)
        
        # all full views are counted (like downloads)
        response = self.assertGet('view_resource', pk=resource.pk)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 2)

    def test_submit_item_anon(self):
        """Test if we can upload a file when we're not logged in,
        shouldn't be allowed and shouldn't work"""
        num = Resource.objects.count()
        
        self.assertGet('resource.upload', status=403)
        self.assertPost('resource.upload', data=self.data, status=403)
        self.assertEqual(Resource.objects.count(), num)

    def test_drop_item_anon(self):
        """Drag and drop file (ajax request) when not logged in - shouldn't work"""
        num = Resource.objects.count()
        
        self.assertGet('resource.drop', status=403)
        self.assertPost('resource.drop', data={
          'name': "New Name",
          'download': self.download,
        }, status=403)
        self.assertEqual(Resource.objects.count(), num)
    
    def test_paste_text_anon(self):
        """Test pasting a valid text when logged out (fail)"""
        num = Resource.objects.count()
        data = {'download': "foo" * 100,}
        
        self.assertGet('pastebin', status=403)
        self.assertPost('pastebin', data=data, status=403)
        self.assertEqual(Resource.objects.count(), num)
    
        shortdata = {'download': "blah" * 5}
        response = self.assertPost('pastebin', data=shortdata, status=403)
    
    def test_like_item_anon(self):
        """Like a gallery item when logged out should fail"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource!")
        num_likes = resources[0].liked
        
        response = self.assertGet('resource.like', pk=resources[0].pk, like='+')
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(resources[0].liked, num_likes)
        
        response = self.assertGet('resource.like', pk=resources[0].pk, like='-')
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(resources[0].liked, num_likes)
        
    def test_like_unpublished_item_anon(self):
        """Like an unpublished gallery item when logged out should fail"""
        resources = Resource.objects.filter(published=False)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource!")
        num_likes = resources[0].liked
        
        response = self.assertGet('resource.like', pk=resources[0].pk, like='+')
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(resources[0].liked, num_likes)
    
    def test_publish_item_anon(self):
        """Make sure we can't publish resources when logged out"""
        resources = Resource.objects.filter(published=False)
        resource = resources[0]
        
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource")

        # check GET
        response = self.assertGet('publish_resource', pk=resource.pk, status=403)
        
        # check POST
        response = self.assertPost('publish_resource', pk=resource.pk, status=403)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, False)
    
    def test_download_anon(self):
        """Download the actual file"""
        resources = Resource.objects.filter(published=True, downed=0)
        self.assertGreater(resources.count(), 0,
                           'Create a public resource with 0 downloads')
        resource = resources[0]
        response = self.assertGet('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False, status=302)

        filename = resource.download.url.split('/')[-1]
        self.assertEqual(response.url, 'http://testserver/dl/test/' + filename)

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 1)
        
        # every download should increment the counter
        response = self.assertGet('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False)
        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 2)

    def test_edit_item_anon(self):
        """Test that we can't edit any items when we are logged out"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource!")
        resource = resources[0]
        desc = resource.description
        
        # check GET
        response = self.assertGet('edit_resource', pk=resource.pk, status=403)
        
        # check POST
        response = self.assertPost('edit_resource', pk=resource.pk, data=self.data, status=403)
        self.assertEqual(resource.description, desc)
    
    def test_delete_item_anon(self):
        """Make sure that we can't delete resources when we are logged out"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource")
        resource = resources[0]
        
        # check GET
        response = self.assertGet('delete_resource', pk=resource.pk, status=403)
        
        # check POST
        response = self.assertPost('delete_resource', pk=resource.pk, status=403)
        self.assertEqual(resource, Resource.objects.get(pk=resource.pk))

    def test_video_view(self):
        """Make sure video links embed a vieo feature"""
        self.assertTrue(video_embed('http://youtube.com/watch?v=01234567911'))
        for resource in Resource.objects.filter(link__contains='VideoTag'):
            response = self.assertGet('resource', pk=resource.pk)
            self.assertContains(response, '<iframe')
            self.assertContains(response, 'VideoTag')

    def test_endorsement(self):
        """Make sure GPG and Hashes work for downloads"""
        self.assertEndorsement(signature='')
        self.assertEndorsement(Resource.ENDORSE_HASH, signature__contains='good.md5')
        self.assertEndorsement(Resource.ENDORSE_SIGN, signature__contains='good.sig')
        self.assertEndorsement(signature__contains='bad')


