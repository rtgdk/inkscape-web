from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from datetime import date

from .models import Resource, ResourceFile, License


class ResourceUserTests(TestCase):
    fixtures = ['test-auth', 'licenses', 'categories', 'quota', 'resource-tests']

    def setUp(self):
        self.client = Client()
        self.client.login(username='user', password='123456')

    def _get(self, url_name, **kw):
        return self.client.get(reverse(url_name, kwargs=kw), {}, follow=True)

    def test_view_my_item(self):
        target = ResourceFile.objects.get(pk=1)
        response = self._get('resource', pk=target.pk)
        print response

class ResourceAnonTests(TestCase):
    """Test all anonymous functions"""
    fixtures = ['test-auth', 'licenses', 'categories', 'quota', 'resource-tests']

# Required tests:
#
# view_item
# submit_item
# not_logged_in_submit (fail)
# no_more_quota_submit (fail)
# submit_pastebin
# edit_item
# mark_favorite
# mark_not_loggedin (fail)
# mark_own_item (fail)
# download_item
# fillsize_item
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
