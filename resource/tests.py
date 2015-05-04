from django.contrib.auth.models import Group, User, UserManager
from django.contrib.auth import authenticate
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from user_sessions.utils.tests import Client
from datetime import date

from .models import Resource, ResourceFile, License, Quota
from .forms import ResourceFileForm
from django.core.files.storage import default_storage

class BaseCase(TestCase):
    fixtures = ['test-auth', 'licenses', 'categories', 'quota-tests', 'resource-tests']

    def _get(self, url_name, **kw):
        return self.client.get(reverse(url_name, kwargs=kw), {}, follow=True)
      
    def _post(self, url_name, data=None, **kw):
        return self.client.post(reverse(url_name), data, kwargs=kw)


class ResourceUserTests(BaseCase):
    def setUp(self):
        super(ResourceUserTests, self).setUp()
        self.client = Client()
        self.user = authenticate(username='tester', password='123456')
        self.client.login(username='tester', password='123456')

    def test_view_my_public_item(self):
        """Testing item view and template for public own items"""
        #make sure we own the file and it's public
        resource = Resource.objects.get(pk=1)
        resource.published = True
        resource.user = self.user
        resource.save()
        
        target = ResourceFile.objects.get(pk=1)
        
        response = self._get('resource', pk=target.pk)
        self.assertEqual(response.context['object'], target)
        self.assertContains(response, 'file1.svg')# for suv ;)
        self.assertContains(response, 'Resource One')
        self.assertContains(response, 'Big description for Resource One')
        self.assertContains(response, str(self.user))
        self.assertEqual(response.context['object'].viewed, 1)
        
    def test_view_my_unpublished_item(self):
        """Testing item view and template for non-published own items"""
        #make sure we own the file and unpublish
        resource = Resource.objects.get(pk=1)
        resource.user = self.user
        resource.published = False
        resource.save()
        
        target = ResourceFile.objects.get(pk=1)
        
        response = self._get('resource', pk=target.pk)
        self.assertEqual(response.context['object'], target)
        self.assertContains(response, 'file1.svg')
        self.assertContains(response, 'Resource One')
        self.assertContains(response, 'Big description for Resource One')
        self.assertContains(response, str(self.user))
        self.assertEqual(response.context['object'].viewed, 1)    
        
    def test_view_someone_elses_public_item(self):
        """Testing item view and template for someone elses public resource"""
        #make sure we don't own the file
        resource = Resource.objects.get(pk=1)
        if self.user.pk == 1:
            self.fail("Please use or set another user id for this test!")
        resource.user = User.objects.get(pk=1) #not current user, hopefully.
        resource.published = True
        resource.save()
        
        target = ResourceFile.objects.get(pk=1)
        
        response = self._get('resource', pk=target.pk)
        self.assertEqual(response.context['object'], target)
        self.assertContains(response, 'file1.svg')
        self.assertContains(response, 'Resource One')
        self.assertContains(response, 'Big description for Resource One')
        self.assertContains(response, str(resource.user) )
        self.assertEqual(response.context['object'].viewed, 1)

    def test_view_someone_elses_unpublished_item(self):
        """Testing item view for someone elses non-public resource: Page not found"""
        #make sure we don't own the file
        resource = Resource.objects.get(pk=1)
        print 'The file is public: ', resource.published
        if self.user.pk == 1:
            self.fail("Please use or set another user id for this test!")
        print 'it belongs to: ', resource.user
        resource.user = User.objects.get(pk=1) #not current user, hopefully.
        resource.published = False
        resource.save()
        
        target = ResourceFile.objects.get(pk=1)
        
        response = self._get('resource', pk=target.pk)
        print 'I am: ', self.user
        print 'The file belongs to: ', resource.user
        print 'The file is public: ', resource.published
        print response
        self.assertEqual(response.status_code, 404)
    
    def test_submit_item_GET(self):
        """Tests the GET view for uploading a new resource file"""
        
        response = self._get('resource.upload')
        self.assertIsInstance(response.context['form'], ResourceFileForm)
        # more?
        
   
    def test_submit_item_POST(self):
        """Tests the POST view and template for uploading a new resource file"""
        #This part could be repeated for different inputs/files to check for errors and correct saving, subtests? 
        #Could become a mess if all are in one test.
        num_resources_before = Resource.objects.all().count()
        
        with open('./fixtures/media/test/file1.svg') as some_file, open('./fixtures/media/test/preview3.png') as thumbnail:
            response = self._post('resource.upload', 
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
        
    def test_submit_item_GET_not_loggedin(self):
        """Test if we can access the file upload form when we're not logged in - shouldn't be allowed"""
        
        self.client.logout()
        
        response = self._get('resource.upload')
        self.assertEqual(response.status_code, 403)
        
    def test_submit_item_POST_not_loggedin(self):
        """Test if we can upload a file when we're not logged in - shouldn't be allowed"""
        
        self.client.logout()
        
        with open('./fixtures/media/test/file1.svg') as some_file, open('./fixtures/media/test/preview3.png') as thumbnail:
          response = self._post('resource.upload',
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
        
        small_quota = Quota.objects.all()[0]  #the first one is the default quota here
        small_quota.size = 50 #50kb
        small_quota.save()
        
        quota = self.user.quota() #now should be 50 kb

        #create a file > 50kb, see NOTES
        
        # with open('./fixtures/media/test/file1.svg') as some_file:
        #       response = self._post('resource.upload', data={'download': some_huge_file, 
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

    def edit_item_being_the_owner_GET(self):
        """Test if we can access the item edit page for our own item"""
        
        #make sure we own the file
        resource = Resource.objects.get(pk=1)
        resource.user = self.user # current user
        resource.save()
        
        target = ResourceFile.objects.get(pk=1)
        
        response = self._get('edit_resource', pk=target.pk)
        self.assertIsInstance(response.context['form'], ResourceFileForm)
        self.assertContains(response, target.name)

    def edit_item_being_the_owner_POST(self):
        """Test if we can edit an item which belongs to us"""
        pass
      
    def edit_item_logged_out_GET(self):
        """Test that we can't access the edit form for our items when we are logged out"""
        pass
      
    def edit_item_logged_out_POST(self):
        """Test that we can't edit our items when we are logged out"""
        pass
      
    def edit_item_by_other_user_GET(self):
        """Check that another user can't access the edit form for my items"""
        pass
      
    def edit_item_by_other_user_POST(self):
        """Check that another user can't edit my items"""
        pass

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
# edit_item: started
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

#NOTES

#TODO
#add some contents to the fixture's svg / png files? Make sure submitting a file actually works.

#create a temporary File that is automatically removed after use:   
#import tempfile
#import os

#temp = tempfile.NamedTemporaryFile(suffix='.txt', 
                                   #prefix='testfile',
                                   #dir='/tmp',
                                   #)
#temp.write('Some data'*300)
#temp.seek(0)
    
#print temp.read()
#print 'temp:', temp
#print 'temp.name:', temp.name

#temppath = temp.name
#print os.path.getsize(temppath)
#temp.close()   
