# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-01-24"
__author__ = "diabeteman"



import os.path

ROOT = os.path.abspath(os.path.dirname(__file__))
def resolvePath(relativePath):
    return str(os.path.join(ROOT, relativePath)).replace("\\", "/")

###############################################################################
# ECM SETTINGS
ALL_GROUP_IDS = [ 1 << i  for i in range(17)] # generates all titleIDs
DIRECTOR_GROUP_ID = 1 << 16 # 65536 (it is twice the max titleID)
DIRECTOR_GROUP_NAME = "Directors"
CRON_USERNAME = "cron"
EVE_DB_FILE = resolvePath('db/EVE.db')
EVE_API_VERSION = "2"
ECM_BASE_URL = "http://127.0.0.1:8000"
ACCOUNT_ACTIVATION_DAYS = 2

###############################################################################
# DJANGO SPECIFIC SETTINGS
DEBUG = True # turn this to False when on production !!!
ADMINS = ()
# for development, you can use python dummy smtp server, run this command:
# >>> python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_HOST_USER = "" 
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = "admin@eve-corp-management.org"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': resolvePath('db/ECM.db')
    }
}

USE_I18N = False # for optimizatrion
LOCAL_DEVELOPMENT = True
APPEND_SLASH=False
TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS
TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
MEDIA_ROOT = resolvePath('media/')
MEDIA_URL = "/m/"
SECRET_KEY = 'u-lb&sszrr4z(opwaumxxt)cn*ei-m3tu3tr_iu4-8mjw+9ai^'
ROOT_URLCONF = 'ecm.urls'
LOGIN_URL = '/account/login'
LOGOUT_URL = '/account/logout'
LOGIN_REDIRECT_URL = '/account'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
# file system cache backend path for unix
#CACHE_BACKEND = 'file:///var/tmp/django_cache'
# file system cache backend path for windows
#CACHE_BACKEND = 'file://C:/Users/diabeteman/AppData/Local/Temp/django_cache'
#NO CACHE FOR DEV USAGE
CACHE_BACKEND = 'dummy://'

TEMPLATE_DIRS = (
        resolvePath('templates/'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "ecm.view.context_processors.corporation_name",
)

FIXTURE_DIRS = (
    resolvePath("fixtures/auth/"),
)

CAPTCHA_LENGTH = 5
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.databrowse',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.databrowse',
    'django.contrib.sessions',
    'django.contrib.sites',
    
    'captcha',
    
    'ecm.data.assets',
    'ecm.data.corp',
    'ecm.data.roles',
    'ecm.data.common',
    'ecm.data.scheduler',
    'ecm.data.accounting',
)

###############################################################################
# LOGGING SETTINGS
if not os.path.exists(resolvePath('logs')):
    os.makedirs(resolvePath('logs'))
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'ecm_formatter': {
            'format': '%(asctime)s [%(levelname)-5s] %(name)s - %(message)s'
        },
    },
    'handlers': {
        'ecm_file_handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'ecm_formatter',
            'level': 'INFO',
            'filename': resolvePath('logs/ecm.log'),
            'when': 'midnight', # roll over each day at midnight
            'backupCount': 15, # keep 15 backup files
        },
        'ecm_console_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'ecm_formatter',
            'level': 'DEBUG',
        }
    },
    'loggers': {
        'ecm': {
                                            # remove console handler on production
            'handlers':['ecm_file_handler', 'ecm_console_handler'], 
            'propagate': True,
            'level':'DEBUG',
        },
    }
}
