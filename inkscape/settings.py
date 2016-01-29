# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.conf import global_settings
import sys
import os

gettext = lambda s: s

MAX_PREVIEW_SIZE = 5 * 1024 * 1024

SERVE_STATIC = True

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
    ('da', 'Danish'),
    ('fr', 'French'),
    ('nl', 'Dutch'),
    ('it', 'Italian'),
    ('es', 'Spanish'),
    ('pt', 'Portuguese'),
    ('pt-br', 'Brazilian Portuguese'),
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

# Place where uploaded files and static can be seen online
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
EXTRA_APPS = []

#
# --- Above this line, settings can be over-ridden for deployment
# 
from inkscape import *

sys.path.insert(0, os.path.join(PROJECT_PATH, 'libs'))

HOST_ROOT = SITE_ADDRESS
SITE_ROOT = "http://%s" % SITE_ADDRESS

TEMPLATE_DEBUG = DEBUG

# Place where files can be uploaded
# Place where media can be served from in development mode
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'data', 'media', '')
STATIC_ROOT = os.path.join(PROJECT_PATH, 'data', 'static')
FIXTURE_DIRS = os.path.join(PROJECT_PATH, 'data', 'fixtures'),
IRCBOT_PID = os.path.join(PROJECT_PATH, 'data', 'ircbot.pid')

LOCALE_PATHS = (
  os.path.join(PROJECT_PATH, 'data', 'locale', 'website'),
)
ROSETTA_EXTRA_PATHS = (
  os.path.join(PROJECT_PATH, 'data', 'locale', 'inkscape'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',  
    'django.template.loaders.app_directories.Loader',  
)
if not DEBUG:
    # Add a template loader if not in debug
    TEMPLATE_LOADERS = (('django.template.loaders.cached.Loader', TEMPLATE_LOADERS),)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'inkscape.context_processors.version',
    'inkscape.context_processors.design',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
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
    'inkscape.middleware.AutoBreadcrumbMiddleware',
    'user_sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'inkscape.middleware.CsrfWhenCaching',
    'cms.middleware.language.LanguageCookieMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cmsdiff.middleware.CommentMiddleware',
    'cmsdiff.middleware.ObjectToolbarMiddleware',
    'social_auth.middleware.SocialAuthExceptionMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'person.middleware.SetLastVisitMiddleware',
)

# Add caching middleware only if we're live.
if not DEBUG:
    MIDDLEWARE_CLASSES = \
      ('django.middleware.cache.UpdateCacheMiddleware',) + \
      MIDDLEWARE_CLASSES + \
      ('django.middleware.cache.FetchFromCacheMiddleware',)

ROOT_URLCONF = 'inkscape.urls'

INSTALLED_APPS = (
    'inkscape', # Goes first
    'django.contrib.sites',
    'django.contrib.auth',
    'user_sessions',
    'registration',
    'social_auth',
    'person',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.redirects',
    'django.contrib.staticfiles',
    'ajax_select',
    'haystack',
    'cmsdiff',
    'reversion',
    'pile',
    #'cmsrosetta',
    'treebeard',
    'cms',
    'menus',
    'sekizai',
    'pagination',
    'djangocms_text_ckeditor',
    'djangocms_file',
    'djangocms_picture',
    'djangocms_link',
    'cmsplugin_toc',
    'cmsplugin_search',
    'cmsplugin_news',
    'cmstabs',
    'docs',
    'resource',
    'moderation',
    'projects',
    'releases',
    'django_comments',
    'django_mailman',
    'alerts',
) + tuple(EXTRA_APPS)

SESSION_ENGINE = 'user_sessions.backends.db'

MODERATED_MODELS = (
    ('auth.user',               _('Website User')),
    ('resource.resourcefile',   _('Gallery Resource')),
    ('django_comments.comment', _('User Comment')),
)

AUTH_USER_MODEL = 'auth.User'

# activate automatically filled menues and deactivate redirection to English for non-translated cms pages
CMS_LANGUAGES = {
    'default': {
        'fallbacks': ['en'],
        'public': True,
        'hide_untranslated': False, # fill the menu
        'redirect_on_fallback': False, # stay in the selected language instead of going to /en/ urls
    }
}

CMS_TEMPLATES = (
    ('cms/normal.html',   _('Normal Page')),
    ('cms/withside.html', _('Side Bar Page')),
    ('cms/front.html',    _('Three Column Page')),
    ('cms/super.html',    _('Full Screen')),
    ('cms/develop.html',  _('Developer Page')),
)

# activate automatic filling-in of contents for non-translated cms pages
CMS_PLACEHOLDER_CONF = {placeholder : {'language_fallback': True,} for placeholder in [
    'normal_template_content', 
    'front_body', 
    'column_one', 
    'column_two', 
    'column_three', 
    'sidebar_template_content',]
}

CMS_APPLICATIONS_URLS = (
    ('cmsplugin_news.urls', 'News'),
)
CMS_APPHOOKS = (
   'cmsplugin_news.cms_app.NewsAppHook',
   'inkscape.cms_app.SearchApphook',
)
CMS_NAVIGATION_EXTENDERS = (
    ('cmsplugin_news.navigation.get_nodes','News navigation'),
)

CKEDITOR_SETTINGS = {
    'disableNativeSpellChecker': False,
    'browserContextMenuOnCtrl': True,
}

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Custom pipeline to insert openid to oauth2 migration
SOCIAL_AUTH_PIPELINE = (
  'social_auth.backends.pipeline.social.social_auth_user',
  'inkscape.google_pipeline.migrate_from_openid',
  'social_auth.backends.pipeline.user.get_username',
  'social_auth.backends.pipeline.user.create_user',
  'social_auth.backends.pipeline.social.associate_user',
  'social_auth.backends.pipeline.social.load_extra_data',
  'social_auth.backends.pipeline.user.update_user_details',
)


ACCOUNT_ACTIVATION_DAYS = 7

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_sa_user'
LOGIN_URL          = '/user/login/'
LOGIN_ERROR_URL    = '/user/login/'
LOGIN_REDIRECT_URL = '/user/'

RECAPTCHA_USE_SSL = True

OPENID_REDIRECT_NEXT = '/accounts/openid/done/'

OPENID_AX = [{
  "type_uri": "http://axschema.org/contact/email",
  "count": 1,
  "required": True,
  "alias": "email",
  },{
  "type_uri": "http://axschema.org/schema/fullname",
  "count":1 ,
  "required": False,
  "alias": "fname",
}]

OPENID_AX_PROVIDER_MAP = {
  'Default': {
    'email': 'http://axschema.org/contact/email',
    'fullname': 'http://axschema.org/namePerson',
    'nickname': 'http://axschema.org/namePerson/friendly',
  },
}

FACEBOOK_EXTENDED_PERMISSIONS = ['email']

GEOIP_PATH = os.path.join(PROJECT_PATH, 'data', 'geoip')

# This setting is for django-social-auth
SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'

SENDFILE_BACKEND = 'sendfile.backends.development'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = MEDIA_URL

AJAX_LOOKUP_CHANNELS = {
  'user'    : {'model':'auth.User',             'search_field':'username'},
  'resource': {'model':'resource.ResourceFile', 'search_field':'name'},
  'tags'    : ('resource.lookups', 'TagLookup'),
}

AJAX_SELECT_BOOTSTRAP = False
AJAX_SELECT_INLINES = 'inline'

TEST_RUNNER = 'inkscape.runner.InkscapeTestSuiteRunner'
SILENCED_SYSTEM_CHECKS = ["1_6.W002"]

MIGRATION_MODULES = {
  'djangocms_file': 'djangocms_file.migrations_django',
  'djangocms_link': 'djangocms_link.migrations_django',
  'djangocms_picture': 'djangocms_picture.migrations_django',
  'djangocms_text_ckeditor': 'djangocms_text_ckeditor.migrations_django',
  'cmsplugin_pygments': 'cmsplugin_pygments.migrations_django',
}

ERROR_RATE_LIMIT = 300 # 5 minutes

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['ratelimit'],
        }
    },
    'filters': {
        'ratelimit': {
            '()': 'inkscape.ratelimit.RateLimitFilter',
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# ===== Migration to MySQL Special Code ===== #
# Allows us an extra option for turning off key checks

from django.db.backends.signals import connection_created
import sys

def turn_off_constraints(sender, connection, **kwargs):
    if 'mysql' in connection.settings_dict['ENGINE']\
      and connection.settings_dict.get('FOREIGN_KEY_CHECK') == True\
      and not hasattr(connection, 'fk_check'):
        sys.stderr.write("\n== TURNING OFF MYSQL FOREIGN KEY CHECKS!!==\n\n")
        cursor = connection.cursor()
        cursor.execute('SET foreign_key_checks = 0')
        connection.fk_check = True

connection_created.connect(turn_off_constraints)

