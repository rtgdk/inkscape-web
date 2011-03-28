# coding: utf-8
# Django settings for djink project.
from django.conf import global_settings
from os.path import join, dirname, abspath

INKSCAPE_VERSION = '0.48.1'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Chris Morgan', 'me@chrismorgan.info'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'db.sqlite',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
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

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = join(abspath(dirname(dirname(__file__))), 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'iccj=*n_h03lm!)53e^ze&qudzcyoc+qi8s=$+fj6khix-w&*e'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'djink.versions.versions_context_processor',
    'djink.nav.navigation_context_processor',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'djink.i18n.LocaleSubdomainMiddleware',
    #'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'djink.urls'

APPEND_TRAILING_SLASH = True

TEMPLATE_DIRS = (
    join(dirname(__file__), 'templates').replace('\\', '/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # We may need to use this once we get to db-backed stuff, but the language
    # subdomain stuff will probably be easier managed as a separate field.
    # Could be messy, the way it uses settings.SITE_ID makes it a bit hard.
    #'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'djink',
    'djink.i18n',
    'djink.apps.content',
    'djink.apps.news',
)

RST_SETTINGS_OVERRIDES = {
    'file_insertion_enabled': 0,
    'raw_enabled': 0,
    'initial_header_level': 2,
}

CONTENT_PATH = join(dirname(dirname(__file__)), 'content')
NEWS_PATH = join(dirname(dirname(__file__)), 'news')

HOST_ROOT = 'djink.chrismorgan.info'

# Development users: add www.localhost, en.localhost, de.localhost, etc. to
# your system's HOSTS file and create local_settings.py next to this file with
# this line in it::
#
#     HOST_ROOT = 'localhost:8000'
#
# Then i18n should magically start working. If you don't do this, you'll be
# stuck in English, but it will work.

try:
    from local_settings import *
except ImportError:
    pass
