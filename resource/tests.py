from django.contrib.auth.models import Group, User, UserManager
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from user_sessions.utils.tests import Client
from datetime import date

from .models import Resource, ResourceFile, License, Quota
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
        
    def test_submit_item_not_loggedin(self):
        """Test if we can upload a file when we're not logged in - shouldn't be allowed"""
        
        self.client.logout() # Can't login, so logout doesn't work...
        
        response = self._get('resource.upload')
        self.assertEqual(response.status_code, 403)
        
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
        print quota
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

#NOTES
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
