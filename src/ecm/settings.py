# Copyright (c) 2010-2011 Robin Jarry
# 
# This file is part of EVE Corporation Management.
# 
# EVE Corporation Management is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# EVE Corporation Management is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
# 
# You should have received a copy of the GNU General Public License along with 
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2010-01-24"
__author__ = "diabeteman"

import os.path

ROOT = os.path.abspath(os.path.dirname(__file__))
def resolvePath(relativePath):
    return str(os.path.join(ROOT, relativePath)).replace("\\", "/")

###############################################################################
# ECM SETTINGS
ALL_GROUP_IDS = [ 1 << i  for i in range(17) ] # generates all titleIDs
DIRECTOR_GROUP_ID = 1 << 16 # 65536 (it is twice the max titleID)
DIRECTOR_GROUP_NAME = "Directors"
CRON_USERNAME = "cron"
ADMIN_USERNAME = "admin"
EVE_API_VERSION = "2"
ECM_BASE_URL = "127.0.0.1:8000"
ACCOUNT_ACTIVATION_DAYS = 2
BASIC_AUTH_ONLY_ON_LOCALHOST = False

###############################################################################
# DJANGO SPECIFIC SETTINGS
DEBUG = True # turn this to False when on production !!!
ADMINS = () # to enable email error reporting, put a tuple in there, ('name', email@adddress.com')
# for development, you can use python dummy smtp server, run this command:
# >>> python -m smtpd -n -c DebuggingServer localhost:25
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_HOST_USER = "" 
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
# put a real email address here, if not, emails sent by the server will be discarded by the relay servers
DEFAULT_FROM_EMAIL = "" 

DATABASES = { # see http://docs.djangoproject.com/en/1.3/ref/settings/#databases
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': resolvePath('../db/ECM.db')
    },
    'eve': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': resolvePath('../db/EVE.db')
    }
}

USE_I18N = False # for optimization
LOCAL_DEVELOPMENT = True
APPEND_SLASH = False
TEMPLATE_DEBUG = DEBUG
MANAGERS = ADMINS
TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
MEDIA_ROOT = resolvePath('../media/')
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

CACHES = {
    'default': {
#        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#        'LOCATION': '/var/django/cache',
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

TEMPLATE_DIRS = (
        resolvePath('../templates/'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "ecm.view.context_processors.corporation_name",
    "ecm.view.context_processors.menu",
    "ecm.view.context_processors.version",
)

FIXTURE_DIRS = (
    resolvePath("fixtures/01-auth/"),
    resolvePath("fixtures/02-common/"),
    resolvePath("fixtures/03-corp/"),
    resolvePath("fixtures/04-roles/"),
    resolvePath("fixtures/05-scheduler/"),
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
    'ecm.data.industry',
)

###############################################################################
# LOGGING SETTINGS
if not os.path.exists(resolvePath('../logs')):
    os.makedirs(resolvePath('../logs'))
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
            'filename': resolvePath('../logs/scheduler.log'),
            'when': 'midnight', # roll over each day at midnight
            'backupCount': 15, # keep 15 backup files
        },
        'ecm_console_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'ecm_formatter',
            'level': 'DEBUG',
        },
        'django_mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
        },
        'django_error': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'ecm_formatter',
            'level': 'ERROR',
            'when': 'midnight',
            'backupCount': 15,
            'filename': resolvePath('../logs/error.log'),
        },
    },
    'loggers': {
        'ecm': {                            # remove console handler on production
            'handlers':['ecm_file_handler', 'ecm_console_handler'], 
            'propagate': True,
            'level':'DEBUG',
        },
        'django.request': {
            'handlers': ['django_mail_admins', 'django_error'],
            'propagate': False,
            'level': 'ERROR',
        },
    }
}
