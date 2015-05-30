import os
from datetime import date
from urllib import urlencode

from django.contrib.auth.models import Group, User, UserManager
from django.contrib.auth import authenticate
from django.core import mail
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.test import TestCase

from user_sessions.utils.tests import Client
from django.http import HttpRequest
from user_sessions.backends.db import SessionStore

from .models import Resource, ResourceFile, Category, License, Quota, Gallery, Tag
from .forms import ResourceFileForm, ResourceEditPasteForm, ResourcePasteForm, GalleryForm
from .views import GalleryList

from django.conf import settings

settings.DEBUG = True

class BaseCase(TestCase):
    fixtures = ['test-auth', 'licenses', 'categories', 'quota', 'resource-tests']

    def open(self, filename, *args):
        "Opens a file relative to this test script"
        return open(os.path.join(os.path.dirname(__file__), filename), *args)

    def _get(self, url_name, *arg, **kw):
        "Make a generic GET request with the best options"
        data = kw.pop('data', {})
        method = kw.pop('method', self.client.get)
        follow = kw.pop('follow', True)
        get_param = kw.pop('get_param', None)
        url = reverse(url_name, kwargs=kw, args=arg)
        if get_param:
            url += '?' + get_param 
        return method(url, data, follow=follow)
      
    def _post(self, *arg, **kw):
        "Make a generic POST request with the best options"
        kw['method'] = self.client.post
        return self._get(*arg, **kw)

    def set_session_cookies(self):
        """Set session data regardless of being authenticated"""

        # Save new session in database and add cookie referencing it
        request = HttpRequest()
        request.session = SessionStore('Python/2.7', '127.0.0.1')

        # Save the session values.
        request.session.save()

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.client.cookies[session_cookie] = request.session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }
        self.client.cookies[session_cookie].update(cookie_data)

    def setUp(self):
        "Creates a dictionary containing a default post request for resources"
        super(TestCase, self).setUp()
        self.client = Client()
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
        #self.set_session_cookies() # activate to test AnonymousUser tests, but deactivated mirrors reality

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
        
    #These tests are not finished, as design seems to be in flux, but can be fleshed out if required       
    def test_category_methods(self):
        """Test methods for categories""" 
        cat = Category.objects.get(name="UI Mockup")
        self.assertEqual(cat.value, "ui-mockup")
        self.assertEqual(cat.get_absolute_url(), "/en/gallery/4/")
      
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
      
    def test_mime_type(self):
        #currently seems to think that every image that isn't gif/jpg/png is automatically svg, probably cause for xcf crash (image/xcf)
        pass
      
class ResourceUserTests(BaseCase):
    """Any test of views and requests where a user is logged in."""
    def setUp(self):
        super(ResourceUserTests, self).setUp()
        self.user = authenticate(username='tester', password='123456')
        self.client.login(username='tester', password='123456')

    # Resource Detail View tests:
    def test_view_my_public_item_detail(self):
        """Testing item detail view and template for public own items,
        and make sure the view counter is correctly incremented"""
        #make sure we own the file and it's public
        resources = Resource.objects.filter(published=True, user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a published resource for user %s" % self.user)
        resource = resources[0]
        num_views = resource.viewed
        
        response = self._get('resource', pk=resource.pk)
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
        
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        self.assertContains(response, str(self.user))
        self.assertEqual(response.context['object'].viewed, resource.viewed)
        self.assertEqual(resources.all()[0].viewed, 0)
        # just a suggestion, could also be 1 (but only counting
        # views by the owner is somehow weird)
        
        # number of views should only be incremented once per user session
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(resources.all()[0].viewed, 0)
    
    def test_view_someone_elses_public_item_detail(self):
        """Testing item detail view and template for someone elses public resource:
        license, picture, description, username should be contained, and views should
        be counted correctly"""
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
        self.assertContains(response, resource.license.value)
        self.assertEqual(resources.all()[0].viewed, 1)
        
        # number of views should only be incremented once per user session
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(resources.all()[0].viewed, 1)

    def test_view_someone_elses_unpublished_item_detail(self):
        """Testing item detail view for someone elses non-public resource: 
        Page not found and no incrementing of view number"""
        # Make sure we don't own the resource
        resources = Resource.objects.filter(published=False).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which doesn't belong to %s for this test" % self.user)
        resource = resources[0]
        num = resource.viewed
        
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Resource.objects.get(pk=resource.pk).viewed, num)
    
    def test_view_text_file_detail(self):
        """Check if the text of a textfile is displayed on item view page and its readmore is not"""
        # specific text file resource, description contains a 'Readmore' marker: [[...]]
        resource = Resource.objects.get(pk=2) 

        response = self._get('resource', pk=resource.pk)
        self.assertContains(response, 'Text File Content')
        self.assertContains(response, 'Big description for Resource Two')
        self.assertContains(response, 'readme.txt')
        self.assertNotContains(response, 'And Some More')
    
    # Resource file Full Screen View tests:
    def test_public_resource_full_screen(self):
        """Check that a resource can be viewed in full screen, 
        and that fullview number is incremented when a user with 
        a new session visits a published item in 'full screen glory'"""
        resources = Resource.objects.filter(published=True, fullview=0)
        self.assertGreater(resources.count(), 0,
            "Create a published resource with 0 fullscreen views")
        resource = resources[0]
        
        response = self._get('view_resource', pk=resource.pk, follow=False)
        self.assertEqual(response.url, 'http://testserver/media/test/file3.svg')
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 1)
        
        # The full view counter is untracked so another request will inc too.
        response = self._get('view_resource', pk=resource.pk)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 2)
        
    def test_own_unpublished_resource_full_screen(self):
        """Check that we can look at our unpublished resource in full screen mode"""
        resources = Resource.objects.filter(published=False, user=self.user, fullview=0)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource with 0 fullscreen views for user %s" % self.user)
        resource = resources[0]
        
        response = self._get('view_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 200)
        #resources = Resource.objects.filter(pk=resource.pk)
        self.assertEqual(resources.all()[0].fullview, 0) # just a suggestion, as only the owner would add to views number

    def test_someone_elses_unpublished_resource_full_screen(self):
        """Make sure that fullscreen view for unpublished items 
        doesn't work if they are not ours. Also make sure this 
        doesn't increment the view counter"""
        resources = Resource.objects.filter(published=False, fullview=0).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which doesn't belong to user %s and has 0 full screen views" % self.user)
        resource = resources[0]
        
        response = self._get('view_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 0)
    
    # Readme test:
    def test_readme(self):
        """Download the description as a readme file"""
        resource = Resource.objects.all()[0]
        response = self._get('resource.readme', pk=resource.pk)
        self.assertContains(response, resource.desc)
    
    # Upload view tests:
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
        num = Resource.objects.count() 
        
        response = self._post('resource.upload', data=self.data)
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertEqual(response.status_code, 200)

    def test_submit_gallery_item_POST(self):
        """Test the POST when a gallery is selected"""
        galleries = Gallery.objects.filter(user=self.user)
        self.assertGreater(galleries.count(), 0,
            "Create a gallery for user %s" % self.user)
        gallery = galleries[0]
        num = Resource.objects.count()
        
        response = self._post('resource.upload', gallery_id=gallery.pk, data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertEqual(response.context['object'].gallery, gallery)

    def test_paste_text_POST(self):
        """Test pasting a text, a long one (success) 
        and a short one (fail)"""
        num = Resource.objects.count()
        data = {'download': "foo" * 100,}
        shortdata = {'download': "blah" * 5}
        
        response = self._post('pastebin', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertContains(response, "foofoo")
        
        response = self._post('pastebin', data=shortdata)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertContains(response, "blahblah")
        self.assertIsInstance(response.context['form'], ResourcePasteForm)
        self.assertFormError(response, 'form', 'download', 'Text is too small for the pastebin.')
        
    def test_submit_gallery_failure_POST(self):
        """Test when no permission to submit exists"""
        galleries = Gallery.objects.exclude(user=self.user).exclude(group__in=self.user.groups.all())
        self.assertGreater(galleries.count(), 0,
            "Create a gallery for user other than %s" % self.user)
        gallery = galleries[0]
        num = Resource.objects.count()
        
        response = self._post('resource.upload', gallery_id=gallery.pk, data=self.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Resource.objects.count(), num)

    def test_submit_group_gallery(self):
        """Test the POST when a gallery is group based"""
        galleries = Gallery.objects.filter(group__in=self.user.groups.all())\
                      .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0,
            "Create a group gallery for user %s" % self.user)
        gallery = galleries[0]
        num = Resource.objects.count()
        
        response = self._get('resource.upload', gallery_id=gallery.pk,
            data=self.data)
        self.assertEqual(response.status_code, 200)
        # Gallery is only filled on GET, POST just redirects
        self.assertEqual(response.context['gallery'], gallery)

        response = self._post('resource.upload', gallery_id=gallery.pk,
            data=self.data)
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertEqual(response.context['object'].gallery, gallery) 
        
    def test_drop_item_POST(self):
        """Drag and drop file (ajax request)"""
        num = Resource.objects.count()
        response = self._post('resource.drop', data={
          'name': "New Name",
          'download': self.download,
        })
        self.assertEqual(Resource.objects.count(), num + 1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OK|')

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

    def test_submit_item_unacceptable_license(self):
        """Make sure that categories only accept certain licenses"""
        # Current setting for Screenshots (only 'all rights reserved') might need to be changed.
        categories = Category.objects.filter(visible=True)\
            .exclude(acceptable_licenses=self.data['license'])
        # The selected category MUST be visible or django forms will consider
        # the selection to be None (and likely cause errors)
        self.assertGreater(categories.count(), 0,
            "Create a visible category where license id %s isn't acceptable" % self.data['license'])
        self.data['category'] = categories[0].pk

        num = Resource.objects.count()
        
        response = self._post('resource.upload', data=self.data)
        self.assertEqual(Resource.objects.count(), num)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], ResourceFileForm)
        self.assertFormError(response, 'form', 'license', 'This is not an acceptable license for this category')
    
    # Resource Like tests:
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
        """Like a gallery item which belongs to someone else, and is not public
        - should fail and not change anything in db"""
        resources = Resource.objects.filter(published=False)\
            .exclude(user=self.user, liked__lt=100)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which doesn't belong to user %s" % self.user)

        self.assertNotEqual(resources[0].liked, 1)
        response = self._get('resource.like', pk=resources[0].pk, like='+', follow=False)
        self.assertEqual(response.status_code, 302)

        # This is a sucessful +like so we expect it to recalculate.
        self.assertEqual(resources[0].liked, 1)
        
    def test_like_item_being_owner(self):
        """Like a gallery item which belongs to me should fail"""
        resources = Resource.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource for user %s" % self.user)

        num_likes = resources[0].liked    
        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(resources[0].liked, num_likes)

    # Resource Publish tests:
    def test_publish_item(self):
        """Check that we can publish our own items"""
        resources = Resource.objects.filter(published=False, user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource for user %s" % self.user)
        resource = resources[0]

        response = self._post('publish_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, True)
        
        # Make sure nothing weird will happen when published twice.
        response = self._post('publish_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, True)

    def test_publish_another_persons_item(self):
        """Make sure we can't publish resources which are not ours"""
        resources = Resource.objects.filter(published=False).exclude(user=self.user)
        resource = resources[0]
        
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource which does not belong to user %s" % self.user)

        response = self._get('publish_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, False)

    # Resource Download tests:
    def test_download(self):
        """Download the actual file"""
        resources = Resource.objects.filter(published=True, downed=0)
        self.assertGreater(resources.count(), 0,
                           'Create a public resource with 0 downloads')
        resource = resources[0]
        response = self._get('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/media/test/file3.svg')

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 1)

        #try again, counter should increment again
        response = self._get('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False)

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 2)
        
    def test_download_non_existent_file(self):
        resources = Resource.objects.filter(published=True, downed=0)
        self.assertGreater(resources.count(), 0,
                           'Create a public resource with 0 downloads')
        resource = resources[0]
        response = self._get('download_resource', pk=resource.pk,
                       fn=resource.filename() + 'I_don_t_exist', follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Can not find file &#39;%s&#39;' % (resource.filename() + 'I_don_t_exist'))
        self.assertEqual(response.url, resource.get_absolute_url())

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 0)
        
    def test_download_non_public_file_not_owner(self):
        resources = Resource.objects.filter(published=False).exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
                           'Create a non-public resource with 0 downloads which does not belong to %s' % self.user)
        resource = resources[0]
        num_dl = resource.downed
        response = self._get('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False)

        self.assertEqual(response.status_code, 404)

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, num_dl)
        
    # Resource Edit tests:
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
        resources = Resource.objects.filter(user=self.user)
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
        self.assertNotEqual(resource.description, self.data['desc'])
        
    # Resource Deletion tests:
    def test_delete_own_item(self):
        """Check that we can delete our own items"""
        resources = Resource.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which belongs to user %s" % self.user)
        resource = resources[0]
        
        response = self._post('delete_resource', pk=resource.pk, follow=False)
        
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Resource.DoesNotExist):
            deleted = Resource.objects.get(pk=resource.pk)
        
        deleted = self._get('resource', pk=resource.pk)
        self.assertEqual(deleted.status_code, 404)
        
    def test_delete_another_persons_item(self):
        """Make sure that we can't delete other people's items"""
        resources = Resource.objects.exclude(user=self.user)
        self.assertGreater(resources.count(), 0,
            "Create a resource which does not belong to user %s" % self.user)
        resource = resources[0]
        
        response = self._post('delete_resource', pk=resource.pk)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(resource, Resource.objects.get(pk=resource.pk))

    # Gallery tests
    def test_view_global_gallery(self):
        """Look at the gallery containing every public resource from everyone"""
        # seems the global gallery doesn't use the standard ordering for Resources (-created), but orders by id
        # (which on live should result in the same ordering...)
        # maybe caused by _default_manager in pile/views.py, line 177 ?
        resources = Resource.objects.filter(published=True)#.order_by('pk')# pk for no error
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
        resources = Resource.objects.filter(published=True)
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
        resources = Resource.objects.filter(published=True)
        self.assertGreater(resources.count(), 3,
                           "Create a few public resources for the global gallery")
        
        baseresponse = self._get('resources')
        orderlist = [ordering[0] for ordering in GalleryList.orders]
        self.assertGreater(len(orderlist), 3,
                           "Choose some ordering for your gallery")
        rev_orderlist = [o[1:] if o[0]=='-' else '-' + o for o in orderlist]
        
        #the generator nature of 'orders' in template context doesn't allow us 
        #to use that for testing because it's already 'exhausted'
        
        #make sure the links to the reverse standard order are in the html
        for rev_order in rev_orderlist:
            self.assertContains(baseresponse, rev_order)
            
        #normal order
        for order in orderlist:
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
            
        #reverse order
        for order in rev_orderlist:
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
        resources = Resource.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 1,
                           "Create another resource for user %s" % self.user)
        
        response = self._get('resources', username=self.user.username)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resources[0].name)
        self.assertContains(response, resources[1].name)
        self.assertContains(response, self.user.username)
        self.assertEqual(response.context['object_list'].count(), resources.count())
        self.assertContains(response, '<form method="POST" action="' + reverse('new_gallery'))
        
    def test_view_user_gallery_not_owner(self):
        """Look at all uploads by another user"""
        owner = User.objects.get(pk=2)
        resources = Resource.objects.filter(user=owner, published=True)
        self.assertGreater(resources.count(), 1,
                           "Create another public resource for user %s" % owner)
        
        response = self._get('resources', username=owner.username)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resources[0].name)
        self.assertContains(response, resources[1].name)
        self.assertContains(response, owner.username)
        self.assertEqual(response.context['object_list'].count(), resources.count())
        self.assertNotContains(response, '<form method="POST" action="' + reverse('new_gallery'))
      
    def test_view_group_gallery(self):
        """Look at a gallery belonging to a group of users (team in UI),
        not being a member of that group and not the owner of the gallery"""
        galleries = Gallery.objects.exclude(group=None).exclude(group__in=self.user.groups.all())\
                                   .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0,
                           "Create a group gallery where %s is not a member, and not the owner" % self.user)
        gallery = galleries[0]
        #add a resource to that gallery, so it will show up
        resource_owner = gallery.group.user_set.all()[0]
        resources = Resource.objects.filter(user=resource_owner, published=True)
        self.assertGreater(resources.count(), 0,
                           "Add a public resource for user %s" % resource_owner)
        resource = resources[0]
        gallery.items.add(resource)
        
        # where should the team/group gallery url live? In the creator's username namespace?
        # currently galleries seem to vanish from UI as soon as they are added to a group
        response = self._get('resources', galleries=gallery.slug, username=gallery.user.username)
        
        # resulting in this gallery containing far too many items:
        #print "items: ", gallery.items.all() # 1
        #print response.context['object_list'] # 3
        #print response  # this is - despite the correct link - the all uploads gallery.
        
        self.assertEqual(response.context['object_list'].count(), gallery.items.count())
        
      
    def test_view_group_galleries(self):
        #TODO: find out if it should be 'Group' or 'Team' a gallery is supposed to belong to
        pass
    
    def test_narrow_user_gallery_owner(self):
        """make sure we can choose to see only the resources 
        we want to see in our own gallery"""
        resources = Resource.objects.filter(user=self.user)
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
        """make sure we can choose to see only the resources 
        we are allowed to see in a stranger's gallery"""
        owner = User.objects.get(pk=2)
        resources = Resource.objects.filter(user=owner, published=True)
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
    
    def test_gallery_search(self):
        """Tests the search functionality in galleries"""
        # TODO: update search index somehow first, if that's the reason why it doesn't find anything 
        #       and find out which fields are supposed to be searched
        get_param = urlencode({ 'q' : 'description -Eight +Some'})# depends on fields
        resources = Resource.objects.filter(published=True) # and search corresponding fields here 
        self.assertGreater(resources.count(), 0,
                           "Create a public resource which contains the search term %s")
        
        response = self._get('resources', get_param=get_param)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object_list'], resources)
        self.fail('Finish me!')
      
    def test_move_item_to_gallery(self):
        """Make sure an item can be moved from one gallery to another by its owner"""
        # prepare galleries
        galleries = self.user.galleries.all()
        self.assertGreater(galleries.count(), 1)
        gallery = galleries[0]
        
        # add a resource which belongs to us to a gallery
        resources = Resource.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        gallery.items.add(resource)

        # move that resource to another gallery
        # TODO: we might want to switch to a view name without a dot?
        self._post('resource.move', pk=resource.pk, gallery=galleries[1].pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('url', 'url')# TODO: where do we want to go?
        self.assertEqual(gallery.items.count(), 0)# cached?
        self.assertEqual(galleries[1].items.count(), 1)# cached?
        self.assertEqual(galleries[1][0], resource)# cached?
    
    def test_move_item_to_gallery_not_gal_owner(self):
        """Make sure that we cannot move items into a gallery which isn't ours,
        and not a gallery for a group we're in"""
        # TODO: copy/paste/adapt previous method
        pass
      
    def test_move_item_to_group_gallery_member(self):
        """Make sure that we can move items into a group gallery 
        if we are a member (not owner) of the group"""
        # TODO: copy/paste/adapt previous method
        pass
    
    def test_move_item_to_gallery_not_item_owner(self):
        """Make sure that we cannot move items around that don't belong to us"""
        # TODO: copy/paste/adapt previous method
        pass
    
    def test_copy_item_to_gallery(self):
        """Make sure an item can be copied from one gallery to another by its owner"""
        # prepare galleries
        galleries = self.user.galleries.all()
        self.assertGreater(galleries.count(), 1)
        gallery = galleries[0]
        
        # add a resource which belongs to us to a gallery
        resources = Resource.objects.filter(user=self.user)
        self.assertGreater(resources.count(), 0)
        resource = resources[0]
        gallery.items.add(resource)
        
        # copy that resource to another gallery
        # TODO: we might want to switch to a view name without a dot? Seems those will be deprecated soon.
        self._post('resource.copy', pk=resource.pk, gallery=galleries[1].pk) 
        self.assertEqual(response.status_code, 200)
        self.assertEqual('url', 'url')# TODO: where do we want to go?
        self.assertEqual(gallery.items.count(), 1)# cached?
        self.assertEqual(galleries[1].items.count(), 1)# cached?
        self.assertEqual(galleries[1][0], resource)# cached?
        
    def test_copy_item_to_gallery_not_gal_owner(self):
        """Make sure that we cannot copy items into a gallery which isn't ours, 
        and not a gallery for a group we're in"""
        # TODO: copy/paste/adapt previous method
        pass
      
    def test_copy_item_to_group_gallery_member(self):
        """Make sure that we can copy items into a group gallery 
        if we are a member (not owner) of the group"""
        # TODO: copy/paste/adapt previous method
        pass
      
    def test_copy_item_to_gallery_not_item_owner(self):
        """Make sure we cannot copy items that do not belong to us"""
        # TODO: copy/paste/adapt previous method
        pass
    
    def test_gallery_deletion_own_gallery(self):
        """Test if galleries can be deleted by owner"""
        galleries = Gallery.objects.filter(user=self.user)
        self.assertGreater(galleries.count(), 0, 
                           "Create a gallery which belongs to user %s" % self.user)
        gallery = galleries[0]
        
        response = self._post('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Gallery.DoesNotExist):
            Gallery.objects.get(pk=gallery.pk)

    def test_gallery_deletion_group_gallery(self):
        """Make sure galleries can't be deleted by group member"""
        galleries = Gallery.objects.filter(group__in=self.user.groups.all())\
                                                      .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0, 
                           "Create a gallery for a group in which %s is a member, but not the owner" % self.user)
        gallery = galleries[0]

        response = self._post('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        with self.assertNotRaises(Gallery.DoesNotExist):
            Gallery.objects.get(pk=gallery.pk)
      
    def test_gallery_deletion_group_gallery(self):
        """Make sure galleries can't be deleted by someone unrelated to the gallery"""
        galleries = Gallery.objects.exclude(group__in=self.user.groups.all())\
                                                      .exclude(user=self.user)
        self.assertGreater(galleries.count(), 0, 
                           "Create a group gallery where user %s is neither a group member nor the owner" % self.user)
        gallery = galleries[0]

        response = self._post('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)

    # Gallery RSS tests
    def test_gallery_rss_feed(self):
        """Make sure that every gallery has the correct rss feed"""
        # TODO: currently gets stuck at line 275 in resource.views.py - what does 'object' stand for?
        # Should feeds be dependent on the user that views them? is_visible() in line 277 causes this.
        # Also causes that people get different feeds depending on being logged out or in...
        # Would this confuse feed readers?
        # What's with the additional search term and ordering? Those are currently appended to the rss url
        galleries = Gallery.objects.all()
        
        resources = Resource.objects.filter(published=True)#.order_by('pk')# pk for no error
        response = self._get('resources_rss')
        self.assertEqual(response['Content-Type'][:19], 'application/rss+xml')
        pos = 0
        for resource in resources:
            name = resource.name
            link = resource.get_absolute_url()
            name_pos = response.content.find(str(name), pos)
            link_pos = response.content.find(str(link), name_pos)
            self.assertGreater(link_pos, -1)
            pos = link_pos
        #TODO: 
        #test for search terms and ordering and:
        #response = self._get('resources_rss', category=category)
        #response = self._get('resources_rss', username=username)
        #response = self._get('resources_rss', username=username, category=category)
        #response = self._get('resources_rss', username=username, galleries=gallery.slug)
        #response = self._get('resources_rss', username=username, galleries=gallery.slug, category=category)
        pass

        

class ResourceAnonTests(BaseCase):
    """Tests for AnonymousUser"""
    
    def test_view_public_item_detail_anon(self):
        """Testing item detail view and template for public items,
        and make sure the view counter is correctly incremented"""
        #make sure the file is public
        resources = Resource.objects.filter(published=True)
        self.assertGreater(resources.count(), 0,
            "Create a published resource")
        resource = resources[0]
        num_views = resource.viewed
        
        # the response already contains the updated number
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(response.context['object'], resource)
        self.assertContains(response, resource.filename())
        self.assertContains(response, resource.name)
        self.assertContains(response, resource.description())
        # we don't have any real views saved in the db, so we start with zero
        self.assertEqual(response.context['object'].viewed, 1)
        
        # number of views should only be incremented once per user session
        response = self._get('resource', pk=resource.pk)
        self.assertEqual(Resource.objects.get(pk=resource.pk).viewed, 1)
    
    def test_public_resource_full_screen_anon(self):
        """Check that a resource can be viewed in full screen, 
        and that fullview number is incremented when an 
        anonymous user with a new session visits a published item"""
        resources = Resource.objects.filter(published=True, fullview=0)
        self.assertGreater(resources.count(), 0,
            "Create a published resource with 0 fullscreen views")
        resource = resources[0]
        response = self._get('view_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 1)
        
        # all full views are counted (like downloads)
        response = self._get('view_resource', pk=resource.pk)
        self.assertEqual(Resource.objects.get(pk=resource.pk).fullview, 2)
    
    def test_submit_item_GET_anon(self):
        """Test if we can access the file upload form when we're not logged in - shouldn't be allowed"""
        response = self._get('resource.upload')
        self.assertEqual(response.status_code, 403)
        
    def test_submit_item_POST_anon(self):
        """Test if we can upload a file when we're not logged in,
        shouldn't be allowed and shouldn't work"""
        num = Resource.objects.count()
        
        response = self._post('resource.upload', data=self.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Resource.objects.count(), num)

    def test_drop_item_POST_anon(self):
        """Drag and drop file (ajax request) when not logged in - shouldn't work"""
        num = Resource.objects.count()
        response = self._post('resource.drop', data={
          'name': "New Name",
          'download': self.download,
        })
        self.assertEqual(Resource.objects.count(), num)
        self.assertEqual(response.status_code, 403)
    
    def test_paste_text_POST_anon(self):
        """Test pasting a valid text when logged out (fail)"""
        num = Resource.objects.count()
        data = {'download': "foo" * 100,}
        
        response = self._post('pastebin', data=data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Resource.objects.count(), num)
    
        shortdata = {'download': "blah" * 5}
        response = self._post('pastebin', data=shortdata)
        self.assertEqual(response.status_code, 403)
    
    def test_like_item_anon(self):
        """Like a gallery item when logged out should fail"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource!")
        num_likes = resources[0].liked
        
        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(resources[0].liked, num_likes)
        
    def test_like_unpublished_item_anon(self):
        """Like an unpublished gallery item when logged out should fail"""
        resources = Resource.objects.filter(published=False)
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource!")
        num_likes = resources[0].liked
        
        response = self._get('resource.like', pk=resources[0].pk, like='+')
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertEqual(resources[0].liked, num_likes)
    
    def test_publish_item_anon(self):
        """Make sure we can't publish resources when logged out"""
        resources = Resource.objects.filter(published=False)
        resource = resources[0]
        
        self.assertGreater(resources.count(), 0,
            "Create an unpublished resource")

        response = self._post('publish_resource', pk=resource.pk)
        self.assertEqual(Resource.objects.get(pk=resource.pk).published, False)
    
    def test_download_anon(self):
        """Download the actual file"""
        resources = Resource.objects.filter(published=True, downed=0)
        self.assertGreater(resources.count(), 0,
                           'Create a public resource with 0 downloads')
        resource = resources[0]
        response = self._get('download_resource', pk=resource.pk,
                       fn=resource.filename(), follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://testserver/media/test/file3.svg')

        resource = Resource.objects.get(pk=resource.pk)
        self.assertEqual(resource.downed, 1)

    def test_edit_item_GET_anon(self):
        """Test that we can't access the edit form for our items when we are logged out"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource!")
        resource = resources[0]
        
        response = self._get('edit_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 403)
      
    def test_edit_item_POST_anon(self):
        """Test that we can't edit any items when we are logged out"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource!")
        resource = resources[0]
        desc = resource.description
        
        response = self._post('edit_resource', pk=resource.pk, data=self.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(resource.description, desc)
    
    def test_delete_item_anon(self):
        """Make sure that we can't delete resources when we are logged out"""
        resources = Resource.objects.all()
        self.assertGreater(resources.count(), 0,
            "Create a resource")
        resource = resources[0]
        
        response = self._post('delete_resource', pk=resource.pk)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(resource, Resource.objects.get(pk=resource.pk))
    
    def test_view_all_resources_by_user(self):
        """Look at all uploads from someone, and see only public items"""
        resources = Resource.objects.filter(user=3, published=True)
        self.assertGreater(resources.count(), 0,
                           "Create another resource for user with id 3")
        
        response = self._get('resources', username=User.objects.get(pk=3).username)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, resources[0].name)
        self.assertContains(response, User.objects.get(pk=3).username)
        self.assertEqual(response.context['object_list'].count(), resources.count())
   
    def test_gallery_deletion_anon(self):
        """Make sure galleries can't be deleted by group member"""
        galleries = Gallery.objects.all()
        self.assertGreater(galleries.count(), 0, 
                           "Create a gallery")
        gallery = galleries[0]

        response = self._post('gallery.delete', gallery_id=gallery.id)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Gallery.objects.get(pk=gallery.pk), gallery)
            
# Required tests:
#
# TODO:
# filesize_item: What's this?
# narrow_user_galleries (category): What's this in comparison to: narrow_user_gallery (specific + category)?
# view_group_galleries
# view_group_gallery
# item_breadcrumbs (each variation)
# gallery_breadcrumbs (lots of variations)
# gallery_rss_feed (galleries variations)
# signature (good and bad)
# mirror_flag
# verified_flag
#
# STARTED / DONE(?)
# license_on_gallery_item: started, inside test_view_global_gallery
# license_on_item: started, inside test_view_someone_elses_public_item_detail
# move_item_to_gallery: started
# copy_item_to_gallery: started
# search_galleries: started
# view_user_gallery (specific one): started
# narrow_user_gallery (specific + category): started
# view_item public vs. non-public, too: started
# submit_item: started
# not_logged_in_submit (fail): started
# no_more_quota_submit (fail): started
# submit_pastebin: started
# edit_paste: started
# edit_item: started
# delete item: started
# mark_favorite: started
# mark_not_loggedin (fail): started
# mark_own_item (fail): started
# download_item (non-public, too): started
# view_global_galleries (see multiple users): started
# narrow_global_galleries (category): started
# sort_global_galleries (all four sorts): started (would also work for more than four)
# view_user_galleries: started
# delete gallery: started
# try to download non-existent file: started