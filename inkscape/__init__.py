#
# Copyright 2014, Martin Owens <doctormo@gmail.com>
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
Find and initialize the local_settings.py - this file documents all the
settings and keys which should /NEVER/ be committed to a repository and it
seperates out the sys-admin responsibility from the programmer's.
"""

from shutil import copyfile

import logging
import os

BASE_DIR = os.path.dirname(__file__)
SETTINGS = 'local_settings.py'

try:
  from local_settings import *
except ImportError:
  target = os.path.join(BASE_DIR, SETTINGS)
  if not os.path.exists(target):
      for template in (target + '.template', target[:-3] + '.template'):
          if os.path.exists(template):
              copyfile(template, target)
              break
  try:
      from local_settings import *
  except ImportError:
      logging.error("No settings found and default template failed to load.")
      exit(3)


from django.contrib import admin
from django.contrib.admin import sites
from collections import defaultdict

class MyAdminSite(admin.AdminSite):
    merge = {
      'person': 'auth',
      'django_mailman': 'auth',
      'user_sessions': 'auth',
      'registration': 'auth',
      'social_auth': 'auth',
      'djangocms_snippet': 'cms',
      'cmsdiff': 'cms',
      'cmsplugin_news': 'cmstabs',
      'redirects': 'sites',
    }
    rename = {
      'auth': 'Users and Teams',
      'cms': 'Django CMS',
      'cmstabs': 'Inkscape CMS Extras',
      'List': 'E-Mailing Lists',
      'UserDetails': 'User Profiles',
      'django_comments': 'Comments',
      'UserSocialAuth': 'Social Authentications',
      'TabCategory': 'Tab Categories',
    }

    def index(self, request, **kwargs):
        response = super(MyAdminSite, self).index(request, **kwargs)
        app_list = list(self.regen(response.context_data['app_list']))
        app_list.sort(key=lambda x: x['name'].lower())
        response.context_data['app_list'] = app_list
        return response

    def regen(self, apps):
        to_merge = defaultdict(list)
        for app in apps:
            for model in app.get('models', []):
                model['name'] = self.rename.get(model['object_name'], model['name'])
            if app['app_label'] in self.merge:
                to_merge[self.merge[app['app_label']]] += app.pop('models', [])
            app['name'] = self.rename.get(app['app_label'], app['name'])

        for app in apps:
            if app['app_label'] in to_merge:
                app['models'] += to_merge[app['app_label']]
            if app.get('models', None):
                app['models'].sort(key=lambda x: x['name'].lower())
                yield app

mysite = MyAdminSite()
admin.site = mysite
sites.site = mysite


