# -*- coding: utf-8 -*-

from django.conf import global_settings
from utils import *
import sys
import os

gettext = lambda s: s

MAX_PREVIEW_SIZE = 5 * 1024 * 1024

SOUTH_TESTS_MIGRATE = False
SERVE_STATIC = True
REVISION = '???'

ADMINS = (
    ('Martin Owens', 'doctormo@gmail.com'),
)

MANAGERS = ADMINS

USE_TZ = True
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', 'English'),
    ('de', 'German'),
    ('fr', 'French'),
    ('nl', 'Dutch'),
    ('it', 'Italian'),
    ('es', 'Spanish'),
    ('pt', 'Portuguese'),
    ('cs', 'Czech'),
    ('ru', 'Russian'),
    ('ja', 'Japanese'),
    ('zh', 'Chinese'),
    ('zh-tw', 'Simplified Chinese'),
    ('ko', 'Korean'),
)

SITE_ID = 1
USE_I18N = True
USE_L10N = True
I18N_DOMAIN = 'inkscape'

GOOGLE_ANID = None

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

sys.path.insert(0, os.path.join(PROJECT_PATH, 'libs'))

(VERSION_STRING, INKSCAPE_VERSION) = get_bzr_version(PROJECT_PATH, DEBUG)

LOCALE_PATHS = os.path.join(PROJECT_PATH, 'locale'),

HOST_ROOT = SITE_ADDRESS
SITE_ROOT = "http://%s" % SITE_ADDRESS

TEMPLATE_DEBUG = DEBUG

REV_FILE = os.path.join(PROJECT_PATH, 'data', 'revision')
if os.path.isfile(REV_FILE):
    with open(REV_FILE, 'r') as fhl:
        REVISION = fhl.read().strip()

# Place where files can be uploaded
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'data', 'media/')

# Place where uploaded files can be seen online
MEDIA_URL = '/media/'

# Place where media can be served from in development mode
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')

# Place where static files can be seen online
STATIC_URL = '/static/'

# Out Static url was eaten by the CMS Gru
DESIGN_ROOT = STATIC_ROOT
DESIGN_URL = '/design/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'inkscape.versions.versions_context_processor',
    'inkscape.context_processors.design',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'cms.context_processors.cms_settings',
    'sekizai.context_processors.sekizai',
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_backends',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'user_sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'inkscape.person.middleware.SetLastVisitMiddleware',
)

ROOT_URLCONF = 'inkscape.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django_reset', # forward port of the "reset" command
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.redirects',
    'django.contrib.staticfiles',
    'user_sessions',
    'haystack',
    'reversion',
    'registration',
    'social_auth',
    'cms',     # django CMS itself
    'mptt',    # utilities for implementing a modified pre-order traversal tree
    'menus',   # helper for model independent hierarchical website navigation
    'south',   # intelligent schema and data migrations
    'sekizai', # for javascript and css management
    'pagination',
    'django_cleanup',
    'djangocms_text_ckeditor',
    'djangocms_file',
    'djangocms_picture',
    'djangocms_snippet',
    'djangocms_link',
    'cmsplugin_search',
    'cmsplugin_news',
    'cmsplugin_pygments',
    'cmsplugin_launchpad',
    'cmsplugin_groupphoto',
    'inkscape.extra',
    'inkscape.search',
    'inkscape.person',
    'inkscape.docs',
    'inkscape.resource',
)
SESSION_ENGINE = 'user_sessions.backends.db'

CMS_TEMPLATES = (
    ('normal.html', 'Normal Page'),
    ('front.html', 'Front Page'),
    ('super.html', 'Full Screen'),
)
CMS_APPLICATIONS_URLS = (
    ('cmsplugin_news.urls', 'News'),
)
CMS_APPHOOKS = (
   'cmsplugin_news.cms_app.NewsAppHook',
   'inkscape.search.cms_app.SearchApphook',
)
CMS_NAVIGATION_EXTENDERS = (
    ('cmsplugin_news.navigation.get_nodes','News navigation'),
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SOUTH_MIGRATION_MODULES = {
#    'easy_thumbnails': 'easy_thumbnails.south_migrations',
}

ACCOUNT_ACTIVATION_DAYS = 7

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_sa_user'
LOGIN_URL          = '/person/register/login/'
LOGIN_REDIRECT_URL = '/person/'
LOGIN_ERROR_URL    = '/person/register/login/'

RECAPTCHA_USE_SSL = True

GEOIP_PATH = os.path.join(PROJECT_PATH, 'data', 'geoip')

