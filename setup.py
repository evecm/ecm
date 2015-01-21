#!/usr/bin/env python
# Copyright (c) 2010-2014 AUTHORS
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

import sys

if sys.version_info < (2, 5) or sys.version_info >= (3,):
    sys.stderr.write('ERROR: ecm requires Python versions >= 2.5 and < 3.0\n')
    sys.exit(1)

from setuptools import setup, find_packages
from distutils.command.install import INSTALL_SCHEMES

# Tell distutils not to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

dependencies = [
    'django_simple_captcha >= 0.3',
    'south >= 0.8',
    'django_compressor >= 1.1.2',
    'setuptools',
    'django <= 1.5.7',
    'pytz',
    'pycrypto',
]

setup(
    # GENERAL INFO
    name = 'ecm',
    version = __import__('ecm').VERSION, # dynamically get version from ecm.VERSION.
    description = 'EVE Corp Management is a management and decision-making helper-application for EVE Online.',
    long_description = open('README.md').read(),
    author = 'ggrog',
    author_email = 'ecm@ggrog.com',
    url = 'https://github.com/evecm/ecm',
    download_url = 'https://pypi.python.org/pypi/ecm',
    license = 'GPLv3',
    keywords = ('eve-online', 'django', 'corporation', 'management'),
    platforms = 'any',
    classifiers = (
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Games/Entertainment',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ),

    # DEPENDENCIES
    provides = ['ecm'],
    install_requires = dependencies,

    # CONTENTS
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    entry_points = {
        'console_scripts': ('ecm-admin = ecm.admin.cli:main',),
        'distutils.commands': ('compilemessages = ecm.utils.distrib:CompileMessages',
                               'makemessages = ecm.utils.distrib:MakeMessages'),
    },
)
