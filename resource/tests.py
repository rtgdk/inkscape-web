from django.contrib.auth.models import Group, User, UserManager
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from datetime import date

from .models import Resource, ResourceFile, License
from django.core.files.storage import default_storage

class BaseCase(TestCase):
    fixtures = ['test-auth', 'licenses', 'categories', 'quota-tests', 'resource-tests']

    def _get(self, url_name, **kw):
        return self.client.get(reverse(url_name, kwargs=kw), {}, follow=True)


class ResourceUserTests(BaseCase):
    def setUp(self):
        super(ResourceUserTests, self).setUp()
        self.client = Client()
        
        self.user = User.objects.create_user('MyTestUser', password='123456')
        # regardless if in fixtures or just created, login doesn't work... the user is active and exists.
        print self.client.login(username='MyTestUser', password='123456') #prints false if login didn't work

    def test_view_my_item(self):
        """Testing item view and template"""
        target = ResourceFile.objects.get(pk=1)
        response = self._get('resource', pk=target.pk)
        self.assertEqual(response.context['object'], target)
        self.assertContains(response, 'file1.svg')# for suv ;)
        self.assertContains(response, 'Resource One')
        self.assertContains(response, 'Big description for Resource One')
        self.assertContains(response, 'Staff')
        self.assertEqual(response.context['object'].viewed, 1)
        
    def test_submit_item(self):
        """Tests the get and post views for uploading a new resource file"""
        
        response = self._get('resource.upload')
        self.assertIsInstance(response.context['form'], ResourceFileForm)
        # more?
        
        #This part could be repeated for different inputs/files to check for errors and correct saving, subtests? 
        #Could become a mess if all are in one test.
        some_file = "some data stream" # needs a file in the correct format for post
        some_other_file = "a thumbnail file" # also needs a file in the correct format for post
        
        num_resources_before = Resource.objects.all().count()
        
        response = self.client.post('resource.upload', 
                                    data={'download': some_file, 
                                          'name': 'some file title', 
                                          'link': 'http://www.inkscape.org',
                                          'desc': 'My nice picture',
                                          'category': '2',
                                          'license': '4',
                                          'owner': 'True',
                                          'published': 'on',
                                          'thumbnail': some_other_file})
        
        self.assertEqual(Resource.objects.all().count(), num_resources_before + 1)
        self.assertEqual(response.status_code, 302) #will need to use response.redirect_chain instead
        
        #more assertions for errors depending on user input, need to make sure the language is set correctly to be able to compare 
        #error messages... how? Or should these tests go somewhere else?
        
    def test_submit_item_not_loggedin(self):
        """Test if we can upload a file when we're not logged in - shouldn't be allowed"""
        
        #self.client.logout() # Can't login, so logout doesn't work...
        
        response = self._get('resource.upload')
        self.assertEqual(response.status_code, 403)
        
        with open('./fixtures/media/test/file1.svg') as some_file, open('./fixtures/media/test/preview3.png') as thumbnail:
          response = self.client.post('resource.upload',
                                      data={'download': some_file, 
                                            'name': 'some file title', 
                                            'link': 'http://www.inkscape.org',
                                            'desc': 'My nice picture',
                                            'category': '2',
                                            'license': '4',
                                            'owner': 'True',
                                            'published': 'on',
                                            'thumbnail': thumbnail})
        
        self.assertEqual(response.status_code, 403)
        
    def test_submit_item_quota_exceeded(self):
        """Check that submitting an item which would make the user exceed the quota will fail"""
        
        quota = User.objects.all().filter(username='MyTestUser')[0].quota() #now should be 1Mb
        
        
        # with open('./fixtures/media/test/file1.svg') as some_file:
        #       response = self.client.post('resource.upload', data={'download': some_huge_file, 
        #                                                     'name': 'some file title', 
        #                                                     'link': 'http://www.inkscape.org',
        #                                                     'desc': 'My huge file',
        #                                                     'category': '2',
        #                                                     'license': '4',
        #                                                     'owner': 'True',
        #                                                     'published': 'on',
        #                                                     'thumbnail': ''})
        
        #assert that we get an error message in the form (would be nice, currently we get something weird, I think it's a server error or just the same page again)
        #pass

class ResourceAnonTests(BaseCase):
    """Test all anonymous functions"""
    pass

# Required tests:
#
# view_item #public vs. non-public, too: started
# submit_item: started
# not_logged_in_submit (fail): started
# no_more_quota_submit (fail): started
# submit_pastebin
# edit_item
# mark_favorite
# mark_not_loggedin (fail)
# mark_own_item (fail)
# download_item
# filesize_item
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

#{"pk": 4, "model": "auth.user", "fields":
  #{"username": "whoknowsthepassword", "first_name": "Test", "last_name": "Tester",
   #"is_active": true, "is_superuser": false, "is_staff": false, "groups": [],
   #"password": "pbkdf2_sha256$15000$Y54MfJXgMxo2$/UVYv273/fxGy6+3N5vGLwdhYfDLZzbA5YjGVuwwVWM=",
   #"email": "123456@password.com"}},
