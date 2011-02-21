'''
This file is part of ICE Security Management

Created on 24 jan. 2010
@author: diabeteman
'''

import os.path

ROOT = os.path.abspath(os.path.dirname(__file__))
def resolvePath(relativePath):
    return str(os.path.join(ROOT, relativePath)).replace("\\", "/")


EVE_DB_FILE = resolvePath('db/EVE.db')
EVE_API_VERSION = "2"
LOGGING_CONFIG_FILE = resolvePath("logging.ini")

# Django settings for ism project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('admin', 'admin@ism.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = resolvePath('db/ISM.db')  # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
LOCAL_DEVELOPMENT = True
MEDIA_ROOT = resolvePath('media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/static/"
APPEND_SLASH=False

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = ''

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'u-lb&sszrr4z(opwaumxxt)cn*ei-m3tu3tr_iu4-8mjw+9ai^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfResponseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)


# file system cache backend path for unix
#CACHE_BACKEND = 'file:///var/tmp/django_cache'
# file system cache backend path for windows
#CACHE_BACKEND = 'file://C:/Users/diabeteman/AppData/Local/Temp/django_cache'
#NO CACHE FOR DEV USAGE
CACHE_BACKEND = 'dummy://'


ROOT_URLCONF = 'ism.urls'
LOGIN_URL = '/user/login'
LOGOUT_URL = '/user/logout'
TEMPLATE_DIRS = (
        resolvePath('templates/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "ism.core.context_processors.corporation_name"
)

#TEMPLATE_STRING_IF_INVALID = '%s'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.databrowse',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.databrowse',
    'django.contrib.sessions',
    'django.contrib.sites',
    
    'ism.data.api',
    'ism.data.assets',
    'ism.data.corp',
    'ism.data.roles',
    'ism.data.common',
)


DIRECTOR_GROUP_NAME = "Dirlos"
