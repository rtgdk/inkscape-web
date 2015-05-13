import os
from datetime import date

from django.contrib.auth.models import Group, User, UserManager
from django.contrib.auth import authenticate
from django.core import mail
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.test import TestCase

from user_sessions.utils.tests import Client

from .models import Resource, ResourceFile, Category, License, Quota, Gallery
from .forms import ResourceFileForm, ResourceEditPasteForm

class BaseCase(TestCase):
    fixtures = ['test-auth', 'licenses', 'categories', 'quota', 'resource-tests']

    def open(self, filename, *args):
        "Opens a file relative to this test script"
        return open(os.path.join(os.path.dirname(__file__), filename), *args)

    def _get(self, url_name, *arg, **kw):
        "Make a generic GET request with the best options"
        data = kw.pop('data', {})
        method = kw.pop('method', self.client.get)
        url = reverse(url_name, kwargs=kw, args=arg)
        return method(url, data, follow=True)
      
    def _post(self, *arg, **kw):
        "Make a generic POST request with the best options"
        kw['method'] = self.client.post
        return self._get(*arg, **kw)

    def setUp(self):
        "Creates a dictionary containing a default post request for resources"
        super(TestCase, self).setUp()
        self.download = self.open('fixtures/media/test/file5.svg')
        self.thumbnail = self.open('fixtures/media/test/preview5.png')
        self.data = {
          'download': self.download, 
          'thumbnail': self.thumbnail,
          'name': 'Test Resource Title',
          'link': 'http://www.inkscape.org',
          'desc': 'My nice picture',
          'category': 2,
          'license': 4,
          'owner': 'True',
          'published': 'on',
        }

    def tearDown(self):
        super(TestCase, self).tearDown()
        self.download.close()
        self.thumbnail.close()


class ResourceTests(BaseCase):
    """Test non-request functions and methods"""
    def test_slug(self):
        """Unique slug creation"""
        data = {
          'name': 'Test Resource Title',
          'user': User.objects.get(pk=1),
        }
        one = ResourceFile.objects.create(**data)
        self.assertEqual(one.slug, 'test-resource-title')
        two = ResourceFile.objects.create(**data)
        self.assertEqual(two.slug, 'test-resource-title+0')
        now = ResourceFile.objects.create(**data)
        self.assertEqual(now.slug, 'test-resource-title+1')
        two.delete()
        now = ResourceFile.objects.create(**data)
        self.assertEqual(now.slug, 'test-resource-title+0')

    def test_file_deletion(self):
        """Check that removal of a ResourceFile removes the corresponding Resource and vice versa"""
        resourcefiles = ResourceFile.objects.all()
        self.assertGreater(resourcefiles.count(), 1,
            "Create resource, so there are at least two")

        resourcefile = resourcefiles[0]
        Resource.objects.get(pk=resourcefile.pk).delete()
        with self.assertRaises(ResourceFile.DoesNotExist):
            ResourceFile.objects.get(pk=resourcefile.pk)
            
        resourcefile = resourcefiles[0]
        resourcefile.delete()
        with self.assertRaises(Resource.DoesNotExist):
            Resource.objects.get(pk=resourcefile.pk)

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
        
    #These tests are not real tests, but can be fleshed out if required        
    def test_url_reversing_for_category(self):
        #There's a function for it, but url is not in the urls.py
        #def get_absolute_url(self):
        #return reverse('resource_category', args=[str(self.id)])
        pass
      
    def test_tags(self):
        #currently these are not exposed to the user. 
        #Why do they have a 'parent'? Are circles prevented?
        pass
        
    def test_increment_num_views(self):
        # currently only increments when the user is logged in, as far as testing
        # on local seemed to show
        #def set_viewed(self, session):
        pass
      
    def test_mime_type(self):
        #currently seems to think that every image that isn't gif/jpg/png is automatically svg, probably cause for xcf crash (image/xcf)
        pass
      
    def test_gallery_deletion(self):
        # currently not implemented (view: DeleteGallery)
        pass
      
    def test_move_resource(self):
        # currently not fully implemented (view: MoveResource)
        pass
      
class ResourceUserTests(BaseCase):
    """Any test of views and requests where a user is logged in."""
    def setUp(self):
        super(ResourceUserTests, self).setUp()
        self.client = Client()
        self.user = authenticate(username='tester', password='123456')
        self.client.login(username='tester', password='123456')

    def test_view_my_public_item(self):
        """Testing item view and template for public own items"""
        #make sure we own the file and it's public
        resources = Resource.objects.filter(published=True, user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a published resource for user %s" % self.user)
        resource = resources[0]
        
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        self.assertContains(response, str(self.user))
        self.assertEqual(response.context['object'].viewed, resource.viewed)

    def test_view_text_file(self):
        """Check if the text of a textfile is displayed on item view page and its readmore is not"""
        # specific text file resource, description contains a 'Readmore' marker: [[...]]
        resource = Resource.objects.get(pk=2) 

        response = self._get('resource', pk=resource.pk)
        self.assertContains(response, 'Text File Content')
        self.assertContains(response, 'Big description for Resource Two')
        self.assertContains(response, 'readme.txt')
        self.assertNotContains(response, 'And Some More')

    def test_readme(self):
        """Download the description as a readme file"""
        resource = Resource.objects.all()[0]
        response = self._get('resource.readme', pk=resource.pk)
        self.assertContains(response, resource.desc)

    def test_view_my_unpublished_item(self):
        """Testing item view and template for non-published own items"""
        # make sure we own the file and it is unpublished
        resources = Resource.objects.filter(published=False, user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource for user %s" % self.user)
        resource = resources[0]
        
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        self.assertContains(response, str(self.user))
        self.assertEqual(response.context['object'].viewed, resource.viewed)    
        
    def test_view_someone_elses_public_item(self):
        """Testing item view and template for someone elses public resource"""
        # make sure we don't own the file and it is public
        resources = Resource.objects.filter(published=True).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a published resource that doesn't belong to user %s" % self.user)
        resource = resources[0]
        
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        self.assertContains(response, str(resource.user) )
        self.assertEqual(response.context['object'].viewed, resource.viewed)

    def test_view_someone_elses_unpublished_item(self):
        """Testing item view for someone elses non-public resource: Page not found"""
        
        # Make sure we don't own the resource
        resources = Resource.objects.filter(published=False).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which doesn't belong to %s for this test" % self.user)

        response = self._get('resource', pk=resources[0].pk)
        self.assertEqual(response.status_code, 404)
    
    def test_submit_item_GET(self):
        """Tests the GET view for uploading a new resource file"""
        response = self._get('resource.upload')
        self.assertIsInstance(response.context['form'], ResourceFileForm)
   
    def test_submit_gallery_item_GET(self):
        """Test the GET when a gallery is selected"""
        galleries = Gallery.objects.filter(user=self.user)
        self.assertGreater(galleries.count(), 0,
            "Create a gallery for user %s" % self.user)
        gallery = galleries[0]
        response = self._get('resource.upload', gallery_id=gallery.pk)
        self.assertEqual(response.context['gallery'], gallery)
        self.assertEqual(response.status_code, 200)
        #self.assertContains(response, "name=\"gallery_id\" value=\"%d\"" % gallery.pk)

    def test_submit_gallery_failure_GET(self):
        """Test when no permission to submit exists"""
        galleries = Gallery.objects.exclude(user=self.user).exclude(group__in=self.user.groups.all())
        self.assertGreater(galleries.count(), 0,
            "Create a gallery for user other than %s" % self.user)
        gallery = galleries[0]
        response = self._get('resource.upload', gallery_id=gallery.pk)
        self.assertEqual(response.status_code, 403)

    def test_submit_group_gallery_GET(self):
        """Test the GET when a gallery is group based"""
        galleries = Gallery.objects.filter(group__in=self.user.groups.all())\
                      .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0,
            "Create a group gallery for user %s" % self.user)
        gallery = galleries[0]
        response = self._get('resource.upload', gallery_id=gallery.pk)
        self.assertEqual(response.context['gallery'], gallery)
        self.assertEqual(response.status_code, 200)

    def test_submit_item_POST(self):
        """Tests the POST view and template for uploading a new resource file"""
        # This part could be repeated for different inputs/files to check for errors and correct saving, subtests? 
        # Could become a mess if all are in one test.
        num = Resource.objects.all().count() 
        response = self._post('resource.upload', data=self.data)
        self.assertEqual(Resource.objects.all().count(), num + 1)
        self.assertEqual(response.status_code, 200)

    def test_drop_item_POST(self):
        """Drag and drop file (ajax request)"""
        num = Resource.objects.all().count()
        response = self._post('resource.drop', data={
          'name': "New Name",
          'download': self.download,
        })
        self.assertEqual(Resource.objects.all().count(), num + 1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OK|')

    def test_like_item_not_being_owner(self):
        """Like a gallery item which belongs to someone else"""
        resources = Resource.objects.exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which doesn't belong to user %s" % self.user)

        num_likes = resources[0].liked
        
        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resources[0].liked, num_likes + 1)

        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertEqual(resources[0].liked, num_likes + 1)

        response = self._get('resource.like', pk=resources[0].pk, like='-')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resources[0].liked, num_likes)
        
        # and a second time, for good measure
        response = self._get('resource.like', pk=resources[0].pk, like='-')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resources[0].liked, num_likes)
        
    def test_like_unpublished_item_not_being_owner(self):
        """Like a gallery item which belongs to someone else, and is not public - should fail"""
        resources = Resource.objects.filter(published=False).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which doesn't belong to user %s" % self.user)

        num_likes = resources[0].liked
        
        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(resources[0].liked, num_likes)
        
    def test_like_item_being_owner(self):
        """Like a gallery item which belongs to me should fail"""
        resources = Resource.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource for user %s" % self.user)

        num_likes = resources[0].liked    
        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(resources[0].liked, num_likes)

    def test_publish_item(self):
        """Check that we can publish our own items"""
        resources = Resource.objects.filter(published=False, user=self.user)
        
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource for user %s" % self.user)

        response = self._get('publish_resource', pk=resources[0].pk)
        self.assertEqual(response.status_code, 200)

    def test_publish_another_persons_item(self):
        """Make sure we can't publish resources which are not ours"""
        resources = Resource.objects.filter(published=False).exclude(user=self.user)
        resource = resources[0]
        
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which does not belong to user %s" % self.user)

        response = self._get('publish_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, False)

    def test_download(self):
        """Download the actual file, file3.svg"""
        resource = Resource.objects.get(pk=3)
        response = self._get('download_resource', pk=resource.pk, fn=resource.filename())
        #print response
        # Not sure how to test this properly yet
        # currently returns a 404 error page
        response = self.client.get('/media/test/file3.svg')#this is the response we'd expect, but don't get...
        #print response
        self.fail("Finish this test") #just a marker, so we can't forget

    def test_submit_item_quota_exceeded(self):
        """Check that submitting an item which would make the user exceed the quota will fail"""
        default_quota = Quota.objects.filter(group__isnull=True)[0]
        default_quota.size = 1 # 1024 byte
        default_quota.save()
        name = self.download.name
        quot = self.user.quota()

        self.assertGreater(os.path.getsize(name), quot,
            "Make sure that the file %s is bigger than %d byte" % (name, quot))

        response = self._post('resource.upload', data=self.data)
        self.assertContains(response, "error") #assert that we get an error message in the html (indicator: css class)

    def test_edit_item_being_the_owner_GET(self):
        """Test if we can access the item edit page for our own item"""
        # Make sure we own the file and that it's NOT a pasted text
        resources = Resource.objects.filter(user=self.user).exclude(category=1)
        self.assertGreater(resources.count(), 0,
            "Create a image resource for user %s" % self.user)
        resource = resources[0]
        
        response = self._get('edit_resource', pk=resource.pk)
        self.assertIsInstance(response.context['form'], ResourceFileForm)
        self.assertContains(response, resource.name)

    def test_edit_paste_being_the_owner_GET(self):
        """Test if we can access the paste edit page for our own item"""
        # Make sure we own the file and that it IS a pasted text
        resources = Resource.objects.filter(user=self.user, category=1)
        self.assertGreater(resources.count(), 0,
            "Create a paste resource for user %s" % self.user)
        resource = resources[0]
        
        response = self._get('edit_resource', pk=resource.pk)
        self.assertIsInstance(response.context['form'], ResourceEditPasteForm)
        self.assertContains(response, resource.name)

    def test_edit_item_being_the_owner_POST(self):
        """Test if we can edit an item which belongs to us"""
        resources = Resource.objects.filter(user=self.user, category=1) # only for pastes?
        self.assertGreater(resources.count(), 0,
            "Create a resource for user %s" % self.user)
        resource = resources[0]

        response = self._post('edit_resource', pk=resource.pk) # no changes to resource data?
        self.assertEqual(response.status_code, 200)
      
    def test_edit_item_by_other_user_GET(self):
        """Check that we can't access the edit form for other people's items"""
        #make sure we don't own the file
        resources = Resource.objects.exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which doesn't belong to user %s" % self.user)
        resource = resources[0]
        
        response = self._get('edit_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 403)
        
    def test_edit_item_by_other_user_POST(self):
        """Check that another user can't edit my items"""      
        #make sure we don't own the file
        resources = Resource.objects.exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which doesn't belong to user %s" % self.user)
        resource = resources[0]
        
        response = self._post('edit_resource', pk=resource.pk, data=self.data)
        self.assertEqual(response.status_code, 403)
        
    def test_delete_own_item(self):
        """Check that we can delete our own items"""
        resources = Resource.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which belongs to user %s" % self.user)
        resource = resources[0]
        
        response = self._post('delete_resource', pk=resource.pk)
        
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Resource.DoesNotExist):
            deleted = Resource.objects.get(pk=resource.pk)
        
        deleted_item_view = self._get('resource', pk=resource.pk)
        self.assertEqual(response.status_code, 404)
        
    def test_delete_another_persons_item(self):
        """Make sure that we can't delete other people's items"""
        resources = Resource.objects.exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which does not belong to user %s" % self.user)
        resource = resources[0]
        
        response = self._post('delete_resource', pk=resource.pk)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(resource, Resource.objects.get(pk=resource.pk))

class ResourceAnonTests(BaseCase):
    """Test all anonymous functions"""
    def test_submit_item_GET_not_loggedin(self):
        """Test if we can access the file upload form when we're not logged in - shouldn't be allowed"""
        response = self._get('resource.upload')
        self.assertEqual(response.status_code, 403)
        
    def test_submit_item_POST_not_loggedin(self):
        """Test if we can upload a file when we're not logged in - shouldn't be allowed"""
        response = self._post('resource.upload', data=self.data)
        self.assertEqual(response.status_code, 403)    

    def test_edit_item_logged_out_GET(self):
        """Test that we can't access the edit form for our items when we are logged out"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource!")
        resource = resources[0]
        
        response = self._get('edit_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 403)
      
    def test_edit_item_logged_out_POST(self):
        """Test that we can't edit any items when we are logged out"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource!")
        resource = resources[0]
        
        response = self._post('edit_resource', pk=resource.pk, data=self.data)
        self.assertEqual(response.status_code, 403)
    
    def test_publish_item_logged_out(self):
        """Make sure we can't publish resources when logged out"""
        resources = Resource.objects.filter(published=False)
        resource = resources[0]
        
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource")

        response = self._get('publish_resource', pk=resource.pk)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, False)
    
    def test_delete_item_logged_out(self):
        """Make sure that we can't delete resources when we are logged out"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource")
        resource = resources[0]
        
        response = self._post('delete_resource', pk=resource.pk)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(resource, Resource.objects.get(pk=resource.pk))
    
    def test_like_item_logged_out(self):
        """Like a gallery item when logged out should fail"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource!")
            
        num_likes = resources[0].liked    
        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(resources[0].liked, num_likes)
        
    def test_like_unpublished_item_logged_out(self):
        """Like an unpublished gallery item when logged out should fail"""
        resources = Resource.objects.filter(published=False)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource!")
            
        num_likes = resources[0].liked    
        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(resources[0].liked, num_likes)
   
# Required tests:
#
# view_item #public vs. non-public, too: started
# submit_item: started
# not_logged_in_submit (fail): started
# no_more_quota_submit (fail): started
# submit_pastebin: started
# edit_item: started
# delete item: started
# mark_favorite: started
# mark_not_loggedin (fail): started
# mark_own_item (fail): started
# download_item (non-public, too): started
# filesize_item: What's this? XXX
#
# license_on_item
# license_on_gallery_item
#
# view_global_galleries (see multiple users)
# narrow_global_galleries (category)
# sort_global_galleries (all four sorts)
# view_user_galleries
# narrow_user_galleries (category)
# view_user_gallery (specific one)
# narrow_user_gallery (specific + category)
# view_group_galleries
# view_group_gallery
# search_galleries
# move_item_to_gallery
# copy_item_to_gallery
# 
# item_breadcrumbs (each variation)
# gallery_breadcrumbs (lots of variations)
# gallery_rss_feed (galleries variations)
#
# signature (good and bad)
# mirror_flag
# verified_flag
#
