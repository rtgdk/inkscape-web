# -*- coding: utf-8 -*-
"""
Inkscape's default settings module, will look for a local_settings.py
module to override /some/ of the settings defined here.
"""

from django.utils.translation import ugettext_lazy as _
from django.conf import global_settings
import sys
import os

gettext = lambda s: s

IS_TEST = len(sys.argv) > 1 and sys.argv[1] in ('test', 'autotest')

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
    ('ar', 'Arabic'),
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
    ('sk', 'Slovak'),
    ('ja', 'Japanese'),
    ('zh', 'Simplified Chinese'),
    ('zh-hant', 'Traditional Chinese'),
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

SESSION_COOKIE_AGE = 1209600 # Two weeks
ENABLE_CACHING = False
ENABLE_DEBUG_TOOLBAR = False
ENABLE_DESIGN_TOOLBAR = False
ENABLE_PROFILER_TOOLBAR = False

# Allow realtime updates of pages
#HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

#
# --- Above this line, settings can be over-ridden for deployment
#
from inkscape import *

sys.path.insert(0, os.path.join(PROJECT_PATH, 'libs'))

HOST_ROOT = SITE_ADDRESS
SITE_ROOT = "http://%s" % SITE_ADDRESS

# Place where files can be uploaded
# Place where media can be served from in development mode
LOGBOOK_ROOT = os.path.join(PROJECT_PATH, 'data', 'logs')
DESIGN_ROOT = os.path.join(PROJECT_PATH, 'data', 'static', 'design')
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'data', 'media', '')
STATIC_ROOT = os.path.join(PROJECT_PATH, 'data', 'static')
FIXTURE_DIRS = os.path.join(PROJECT_PATH, 'data', 'fixtures'),
IRCBOT_PID = os.path.join(PROJECT_PATH, 'data', 'ircbot.pid')

STATICFILES_DIRS = []
LOCALE_PATHS = (
  os.path.join(PROJECT_PATH, 'data', 'locale', 'website'),
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [DESIGN_ROOT],
    'OPTIONS': {
      'loaders': [
          'django.template.loaders.filesystem.Loader',
          'django.template.loaders.app_directories.Loader',
      ],
      'context_processors': (
        'inkscape.context_processors.version',
        'social.apps.django_app.context_processors.backends',
        'social.apps.django_app.context_processors.login_redirect',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'django.core.context_processors.i18n',
        'django.core.context_processors.request',
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        'cms.context_processors.cms_settings',
        'sekizai.context_processors.sekizai',
      )
    }
}]

MIDDLEWARE_CLASSES = (
    'inkscape.middleware.CachedRedirects',
    'inkscape.middleware.AutoBreadcrumbMiddleware',
    'inkscape.models.UserOnErrorMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cmsdiff.middleware.ObjectToolbarMiddleware',
    'linaro_django_pagination.middleware.PaginationMiddleware',
    'person.middleware.SetLastVisitMiddleware',
)

# ===== CACHING ===== #

if ENABLE_CACHING or IS_TEST:
    # Caching Middleware caches whole pages, can cause issues
    MIDDLEWARE_CLASSES = \
      ('inkscape.middleware.TrackCacheMiddleware',) + \
      ('django.middleware.cache.UpdateCacheMiddleware',) + \
      MIDDLEWARE_CLASSES + \
      ('django.middleware.cache.FetchFromCacheMiddleware',)

    # Template caching allows quicker fetches
    TEMPLATES[0]['OPTIONS']['loaders'] = [(
        'django.template.loaders.cached.Loader',
        TEMPLATES[0]['OPTIONS']['loaders'],
      )]

ROOT_URLCONF = 'inkscape.urls'

INSTALLED_APPS = (
    'autotest',
    'inkscape', # Goes first
    'person', # Goes next
    'django.contrib.sites',
    'django.contrib.auth',
    'registration',
    'social.apps.django_app.default',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.redirects',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'ajax_select',
    'haystack',
    'pile',
    'treebeard',
    'cms',
    'menus',
    'sekizai',
    'linaro_django_pagination',
    'djangocms_text_ckeditor',
    'djangocms_file',
    'djangocms_link',
    'djangocms_history',
    'cmsplugin_toc',
    'cmsplugin_search',
    'cmsplugin_news',
    'cmsplugin_image',
    'cmsdiff',
    'cmstabs',
    'docs',
    'resources',
    'moderation',
    'projects',
    'releases',
    'django_comments',
    'forums',
    'alerts',
    'logbook',
    'markdown_deux',
)

COMMENTS_APP = 'forums'

MODERATED_MODELS = (
    ('person.user', _('Website User')),
    ('resources.resource', _('Gallery Resource')),
    ('django_comments.comment', _('User Comment')),
)

AUTH_USER_MODEL = 'person.User'

# activate automatically filled menues and deactivate redirection to English
# for non-translated cms pages
CMS_LANGUAGES = {
    'default': {
        'public': True,
        'fallbacks': ['en'],
        'hide_untranslated': False, # fill the menu
        'redirect_on_fallback': False,
        # stay in the selected language instead of going to /en/ urls
    }
}

CMS_TEMPLATES = (
    ('cms/front.html', _('Three Column Page')),
    ('cms/super.html', _('Full Screen')),
    ('cms/normal.html', _('Normal Page')),
    ('cms/develop.html', _('Developer Page')),
    ('cms/withside.html', _('Side Bar Page')),
)

# activate automatic filling-in of contents for non-translated cms pages
CMS_PLACEHOLDER_CONF = {
  placeholder : {'language_fallback': True,} for placeholder in [
    'normal_template_content',
    'front_body',
    'column_one',
    'column_two',
    'column_three',
    'sidebar_template_content']
}

CMS_APPLICATIONS_URLS = (
    ('cmsplugin_news.urls', 'News'),
)
CMS_APPHOOKS = (
   'cmsplugin_news.cms_app.NewsAppHook',
   'inkscape.cms_app.SearchApphook',
)
CMS_NAVIGATION_EXTENDERS = (
    ('cmsplugin_news.navigation.get_nodes', 'News navigation'),
)

CKEDITOR_SETTINGS = {
    'disableNativeSpellChecker': False,
    'browserContextMenuOnCtrl': True,
    'readOnly': False,
}
CKEDITOR_NEWS = {
  'extraPlugins': 'image',
  'filebrowserImageBrowseUrl': '/gallery/pick/',
  'toolbar_HTMLField': [
      ['Undo', 'Redo'], ['ShowBlocks'],
      ['Format', 'Styles', '-', 'RemoveFormat'],
      ['TextColor', 'BGColor', '-', 'PasteText', 'PasteFromWord'],
      ['Maximize', ''],
      '/',
      ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript'],
      ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
      ['Image', '-', 'HorizontalRule'],
      ['Link', 'Unlink'],
      ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Table'],
      ['Source']
    ],
}
CKEDITOR_READONLY = {
    'readOnly': True,
    'disableReadonlyStyling': True,
}

AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.yahoo.YahooOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

ACCOUNT_ACTIVATION_DAYS = 7

SOCIAL_AUTH_DEFAULT_USERNAME = 'new_sa_user'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/user/welcome/'
LOGIN_URL = '/user/login/'
LOGIN_ERROR_URL = '/user/login/'
LOGIN_REDIRECT_URL = '/user/'

RECAPTCHA_USE_SSL = True

OPENID_REDIRECT_NEXT = '/accounts/openid/done/'

OPENID_AX = [{
  "type_uri": "http://axschema.org/contact/email",
  "count": 1,
  "required": True,
  "alias": "email",
  }, {
  "type_uri": "http://axschema.org/schema/fullname",
  "count":1,
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

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

SENDFILE_BACKEND = 'sendfile.backends.development'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = MEDIA_URL

AJAX_LOOKUP_CHANNELS = {
  'user'    : {'model':'person.User', 'search_field':'username'},
  'resource': {'model':'resources.Resource', 'search_field':'name'},
  'tags'    : ('resources.lookups', 'TagLookup'),
}

AJAX_SELECT_BOOTSTRAP = False
AJAX_SELECT_INLINES = 'inline'

TEST_RUNNER = 'inkscape.runner.InkscapeTestSuiteRunner'
SILENCED_SYSTEM_CHECKS = ["1_6.W002"]

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

# ===== Debug Toolbar ===== #

DEBUG_TOOLBAR_PATCH_SETTINGS = True

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TEMPLATE_CONTEXT': True,
    # TURN ON DEBUG VIA A LINK IN THE WEBSITE, SOMETHIN WE CAN ADD TO COOKIES
    'SHOW_TOOLBAR_CALLBACK': lambda req: DEBUG, #'debug' in req.GET or 'debug' in req.META.get('HTTP_REFERER', ''),
    'MEDIA_URL': '/media/debug/',
    'INTERCEPT_REDIRECTS': False,
}
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
)

if ENABLE_DEBUG_TOOLBAR:
    # We're not even going to trust debug_toolbar on live
    INSTALLED_APPS += 'debug_toolbar',

    if ENABLE_PROFILER_TOOLBAR:
        INSTALLED_APPS += 'debug_toolbar_line_profiler',
        DEBUG_TOOLBAR_PANELS += 'debug_toolbar_line_profiler.panel.ProfilingPanel',



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

