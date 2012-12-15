# -*- coding: utf-8 -*-

from django.conf import global_settings
from utils import *
import os

gettext = lambda s: s

SOUTH_TESTS_MIGRATE = False
SERVE_STATIC = True


ADMINS = (
    ('Martin Owens', 'doctormo@ubuntu.com'),
)

MANAGERS = ADMINS

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),    # Guess
    ('de', 'Deutsch'),    # German
    ('fr', 'Français'),   # French
    ('it', 'Italiano'),   # Italian
    ('es', 'Español'),    # Spanish
    ('pt', 'Português'),  # Portuguese
    ('cs', 'Česky'),      # Czech
    ('ru', 'Русский'),    # Russian
    ('ja', '日本'),       # Japanese
)

SITE_ID = 1
USE_I18N = True
USE_L10N = True
I18N_DOMAIN = 'inkscape'

# We import a number of key variables here, if this fails, we don't work!
import logging
try:
  from local_settings import *
except ImportError:
  from shutil import copyfile
  f = 'local_settings.py'
  CODE_PATH = os.path.dirname(os.path.abspath(__file__))
  copyfile(os.path.join(CODE_PATH, f+'.template'), os.path.join(CODE_PATH, f))
  try:
      from local_settings import *
  except ImportError:
      logging.error("No settings found and default template failed to load.")


(VERSION_STRING, INKSCAPE_VERSION) = get_bzr_version(PROJECT_PATH, DEBUG)

LOCALE_PATHS = os.path.join(PROJECT_PATH, 'locale'),

HOST_ROOT = SITE_ADDRESS
SITE_ROOT = "http://%s" % SITE_ADDRESS

TEMPLATE_DEBUG = DEBUG

# Place where files can be uploaded
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'data/media/')

# Place where uploaded files can be seen online
MEDIA_URL = '/media/'

# Place where media can be served from in development mode
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

# Place where static files can be seen online
STATIC_URL = '/static/'
# Out Static url was eaten by the CMS Gru
DESIGN_URL = '/design/'

# Special media directory for admin hosting
ADMIN_MEDIA_PREFIX = '/admin/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'inkscape.versions.versions_context_processor',
    'inkscape.nav.navigation_context_processor',
    'inkscape.context_processors.design',
    'django.contrib.auth.context_processors.auth',
#    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'inkscape.i18n.LocaleSubdomainMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
    'cms.middleware.multilingual.MultilingualURLMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
)

ROOT_URLCONF = 'inkscape.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'inkscape',
    'inkscape.i18n',
    'cms',     # django CMS itself
    'mptt',    # utilities for implementing a modified pre-order traversal tree
    'menus',   # helper for model independent hierarchical website navigation
    'south',   # intelligent schema and data migrations
    'sekizai', # for javascript and css management
    'cms.plugins.file',
    'cms.plugins.picture',
    'cms.plugins.snippet',
    'cms.plugins.video',
    'cms.plugins.twitter',
)

CMS_TEMPLATES = (
    ('super_template.html', 'Full Screen'),
    ('normal_template.html', 'Normal Page'),
)


SERVER_EMAIL         = 'admin@%s' % SITE_ADDRESS
EMAIL_USE_TLS        = True
EMAIL_HOST           = 'smtp.gmail.com'
EMAIL_PORT           = 587

EMAIL_HOST_USER      = 'noone@gmail.com'
EMAIL_HOST_PASSWORD  = 'Nothing'
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME


