# Copyright (c) 2010-2012 Robin Jarry
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
    return os.path.abspath(os.path.join(ROOT, relativePath)).replace("\\", "/")

###############################################################################
################
# ECM SETTINGS #
################

ECM_BASE_URL = "127.0.0.1:8000"

DIRECTOR_GROUP_NAME = "Directors"
CORP_MEMBERS_GROUP_NAME = "Members"
CRON_USERNAME = "cron"
ADMIN_USERNAME = "admin"

EVE_API_VERSION = "2"

ACCOUNT_ACTIVATION_DAYS = 2

PASSWD_MIN_LENGTH = 6
PASSWD_FORCE_SPECIAL_CHARS = False
PASSWD_FORCE_DIGITS = False
PASSWD_FORCE_LETTERS = False

BASIC_AUTH_ONLY_ON_LOCALHOST = False


###############################################################################
###################
# DJANGO SETTINGS #
###################

DEBUG = True # turn this to False when on production !!!

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

##########
# E-MAIL #
##########
# to enable email error reporting, put a tuple in there, ('name', 'email@adddress.com')
ADMINS = ()
# for development, you can use python dummy smtp server, run this command:
# >>> python -m smtpd -n -c DebuggingServer localhost:25
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
# put a real email address here, if not, emails sent by the server
# will be discarded by the relay servers
DEFAULT_FROM_EMAIL = ""
SERVER_EMAIL = ""


##################
# URL MANAGEMENT #
##################
ROOT_URLCONF = 'ecm.urls'

LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout/'
LOGIN_REDIRECT_URL = '/account/'

APPEND_SLASH = True

################
# STATIC FILES #
################

# target dir for the 'collectstatic' command
STATIC_ROOT = resolvePath('../static/')
# value of the {{ STATIC_URL }} variable in templates
STATIC_URL = '/s/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
STATICFILES_DIRS = (
    # aside from looking in each django app, the 'collectstatic' command
    # will look in these directories for static files
    resolvePath('static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)
COMPRESS_OUTPUT_DIR = 'cache'
COMPRESS_CSS_FILTERS = (
    'compressor.filters.css_default.CssAbsoluteFilter',
    #'compressor.filters.csstidy.CSSTidyFilter',
)
#COMPRESS_ENABLED = True

#############
# TEMPLATES #
#############
TEMPLATE_DEBUG = DEBUG
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    # aside from looking in each django app, the template loaders
    # will look in these directories
    resolvePath('templates/'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "ecm.views.context_processors.corporation_name",
    "ecm.views.context_processors.menu",
    "ecm.views.context_processors.version",
)

########
# MISC #
########
USE_I18N = False # for optimization
TIME_ZONE = None # use system default
SECRET_KEY = 'u-lb&sszrr4z(opwaumxxt)cn*ei-m3tu3tr_iu4-8mjw+9ai^'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

CACHES = {
    'default': {
#        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#        'LOCATION': '/var/django/cache/',
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

CAPTCHA_LENGTH = 5
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'

#################
# DJANGO 'APPS' #
#################

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',

    'captcha',
    'south',
    'compressor',
]

ECM_CORE_APPS = [
    'ecm.apps.common',
    'ecm.apps.corp',
    'ecm.apps.hr',
    'ecm.apps.scheduler',
]
INSTALLED_APPS += ECM_CORE_APPS

ECM_PLUGIN_APPS = [
    'ecm.plugins.accounting',
    'ecm.plugins.assets',
    'ecm.plugins.industry',
    'ecm.plugins.shop',
]
INSTALLED_APPS += ECM_PLUGIN_APPS

###########
# LOGGING #
###########

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
            'filename': resolvePath('../logs/ecm.log'),
            #'delay': True, # wait until first log record is emitted to open file
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
            'filename': resolvePath('../logs/error.log'),
            #'delay': True,
            'when': 'midnight',
            'backupCount': 15,
        },
    },
    'loggers': {
        'ecm': {                            # remove console handler on production
            'handlers': ['ecm_file_handler', 'ecm_console_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'ecm.core': {
            'handlers': ['django_error', 'django_mail_admins'],
            'propagate': True,
            'level': 'ERROR',
        },
        'django.request': {
            'handlers': ['django_mail_admins', 'django_error', 'ecm_file_handler'],
            'propagate': False,
            'level': 'ERROR',
        },
    }

}
