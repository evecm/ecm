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

__date__ = '2010-01-24'
__author__ = 'diabeteman'

import os
from ConfigParser import SafeConfigParser

ROOT = os.path.abspath(os.path.dirname(__file__))

def rel_path(pth, root=ROOT):
    return os.path.abspath(os.path.join(root, pth)).replace('\\', '/')
def package_path(package):
    return os.path.abspath(os.path.dirname(__import__(package).__file__))

ECM_PACKAGE = package_path('ecm')
INSTANCE_TEMPLATE_PACKAGE = package_path('ecm.admin.instance_template')

###############################################################################
################
# ECM SETTINGS #
################

CONFIG_FILES = [
    rel_path('settings.ini', root=INSTANCE_TEMPLATE_PACKAGE), # default settings
    rel_path('settings.ini'), # local settings
]

SCHEDULER_MAX_CONCURRENT_TASKS = 1

ACCOUNT_ACTIVATION_DAYS = 2

PASSWD_MIN_LENGTH = 6
PASSWD_FORCE_SPECIAL_CHARS = False
PASSWD_FORCE_DIGITS = False
PASSWD_FORCE_LETTERS = False

BASIC_AUTH_REQUIRED_ON_LOCALHOST = False

config = SafeConfigParser()
if not config.read(CONFIG_FILES):
    raise RuntimeError('Could not find ECM configuration. Looked in %s.' % CONFIG_FILES)

###############################################################################
###################
# DJANGO SETTINGS #
###################

DEBUG = config.getboolean('misc', 'debug')

def get_db_config(prefix):
    engine = config.get('database', prefix + '_engine')
    if engine == 'django.db.backends.sqlite3':
        folder = config.get('database', 'sqlite_db_dir') or rel_path('db/')
        return {'ENGINE': engine, 'NAME': os.path.join(folder, prefix + '.sqlite')}
    else:
        return {
            'ENGINE': config.get('database', prefix + '_engine'),
            'NAME': config.get('database', prefix + '_name'),
            'USER': config.get('database', prefix + '_user'),
            'PASSWORD': config.get('database', prefix + '_password'),
        }

DATABASES = { # see http://docs.djangoproject.com/en/1.3/ref/settings/#databases
    'default': get_db_config('ecm'),
    'eve': get_db_config('eve'),
}

DATABASE_ROUTERS = (
    'ecm.db_routers.ECMDatabaseRouter',
)

SITE_ID = 1

##########
# E-MAIL #
##########
# to enable email error reporting, add tuples in there, ('name', 'email@adddress.com')
ADMINS = [ ('', email) for email in config.get('email', 'admin_email').split() ]

# for development, you can use python dummy smtp server, run this command:
# >>> python -m smtpd -n -c DebuggingServer localhost:25
EMAIL_HOST = config.get('email', 'host')
EMAIL_PORT = config.getint('email', 'port')
EMAIL_USE_TLS = config.getboolean('email', 'use_tls')
EMAIL_HOST_USER = config.get('email', 'host_user')
EMAIL_HOST_PASSWORD = config.get('email', 'host_password')
# put a real email address here, if not, emails sent by the server
# will be discarded by the relay servers
DEFAULT_FROM_EMAIL = config.get('email', 'default_from_email')
SERVER_EMAIL = config.get('email', 'server_email')


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
STATIC_ROOT = config.get('misc', 'static_files_dir') or rel_path('static/')
# value of the {{ STATIC_URL }} variable in templates
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
STATICFILES_DIRS = (
    # aside from looking in each django app, the 'collectstatic' command
    # will look in these directories for static files
    rel_path('static', root=ECM_PACKAGE),
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
COMPRESS_JS_FILTERS = (
    #'compressor.filters.jsmin.JSMinFilter',
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
    rel_path('templates/', root=ECM_PACKAGE),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',

    'ecm.views.context_processors.corporation_name',
    'ecm.views.context_processors.menu',
    'ecm.views.context_processors.version',
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
    'django.contrib.messages.middleware.MessageMiddleware',
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
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'captcha',
    'south',
    'compressor',
]

ECM_CORE_APPS = [
    'ecm.apps.common',
    'ecm.apps.corp',
    'ecm.apps.eve',
    'ecm.apps.hr',
    'ecm.apps.scheduler',
]
INSTALLED_APPS += ECM_CORE_APPS

ECM_PLUGIN_APPS = [
    'ecm.plugins.accounting',
    'ecm.plugins.assets',
    'ecm.plugins.industry',
    'ecm.plugins.shop',
    'ecm.plugins.pos',
]
INSTALLED_APPS += ECM_PLUGIN_APPS

###########
# LOGGING #
###########
LOG_FILES_DIR = config.get('logging', 'log_files_dir') or rel_path('logs/')
if not os.path.exists(LOG_FILES_DIR):
    os.makedirs(LOG_FILES_DIR)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'ecm_formatter': {
            'format': '%(asctime)s [%(levelname)-5s] %(name)s - %(message)s',
        },
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'ecm_formatter',
            'level': 'INFO',
            'filename': os.path.join(LOG_FILES_DIR, 'ecm.log'),
            #'delay': True, # wait until first log record is emitted to open file
            'when': 'midnight', # roll over each day at midnight
            'backupCount': 15, # keep 15 backup files
        },
        'console_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'ecm_formatter',
            'level': 'DEBUG',
        },
        'email_handler': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
        },
        'error_file_handler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'ecm_formatter',
            'level': 'ERROR',
            'filename': os.path.join(LOG_FILES_DIR, 'error.log'),
            #'delay': True,
            'when': 'midnight',
            'backupCount': 15,
        },
    },
    'loggers': {
        'ecm': {                                        # remove console handler on production
            'handlers': ['file_handler', 'email_handler', 'console_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['email_handler', 'error_file_handler', 'file_handler'],
            'propagate': False,
            'level': 'ERROR',
        },
    }

}
