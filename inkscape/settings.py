# coding: utf-8

from django.conf import global_settings
from utils import *
import os

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
    'django.core.context_processors.request',

)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'inkscape.i18n.LocaleSubdomainMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'inkscape.urls'

#APPEND_TRAILING_SLASH = True

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'inkscape',
    'inkscape.i18n',
    'inkscape.content',
    'inkscape.screenshots',
    'inkscape.news',
)

#RST_SETTINGS_OVERRIDES = {
#    'file_insertion_enabled': 0,
#    'raw_enabled': 0,
#    'initial_header_level': 2,
#}


SERVER_EMAIL         = 'admin@%s' % SITE_ADDRESS
EMAIL_USE_TLS        = True
EMAIL_HOST           = 'smtp.gmail.com'
EMAIL_PORT           = 587

EMAIL_HOST_USER      = 'noone@gmail.com'
EMAIL_HOST_PASSWORD  = 'Nothing'
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME


