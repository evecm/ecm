# Copyright (c) 2010-2013 Robin Jarry
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

__date__ = "2013 07 17"
__author__ = "diabeteman"

import os

ROOT = os.path.abspath(os.path.dirname(__file__))

def rel_path(pth, root=ROOT):
    return os.path.abspath(os.path.join(root, pth)).replace('\\', '/')

###################
# DJANGO SETTINGS #
###################

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ecm_feedback',
        'USER': 'ecm_feedback',
        'PASSWORD': 'ecm_feedback',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

SITE_ID = 1

ALLOWED_HOSTS = ['*']

##########
# E-MAIL #
##########
# to enable email error reporting, add tuples in there, ('name', 'email@adddress.com')
ADMINS = [
    ('Admin', 'feedback@eve-corp-management.org')
]

# for development, you can use python dummy smtp server, run this command:
# >>> python -m smtpd -n -c DebuggingServer localhost:25
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_HOST_USER = None
EMAIL_HOST_PASSWORD = None
# put a real email address here, if not, emails sent by the server
# will be discarded by the relay servers
DEFAULT_FROM_EMAIL = 'feedback@eve-corp-management.org'
SERVER_EMAIL = 'feedback@eve-corp-management.org'


##################
# URL MANAGEMENT #
##################
ROOT_URLCONF = 'ecm.utils.usage_feedback.urls'

APPEND_SLASH = True

#############
# TEMPLATES #
#############
STATIC_URL = '/static/'
STATIC_ROOT = rel_path('static/')

TEMPLATE_DEBUG = DEBUG
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    # aside from looking in each django app, the template loaders
    # will look in these directories
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

########
# MISC #
########
USE_I18N = False
USE_L10N = False
USE_TZ = True
SECRET_KEY = 'u-lb&sszrr4z(opwaumxxt)cn*ei-m3tu3tr_iu4-8mjw+9ai^'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


#################
# DJANGO 'APPS' #
#################

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'south',

    'ecm.utils.usage_feedback'
]


###########
# LOGGING #
###########
LOG_FILES_DIR = rel_path('logs/')
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
            'filename': os.path.join(LOG_FILES_DIR, 'feedback.log'),
            'when': 'midnight', # roll over each day at midnight
            'backupCount': 15, # keep 15 backup files
        },
    },
    'loggers': {
        'ecm': {
            'handlers': ['file_handler'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['file_handler'],
            'propagate': False,
            'level': 'ERROR',
        },
    }
}

