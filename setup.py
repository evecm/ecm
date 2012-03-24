#!/usr/bin/env python
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

import ecm
from setuptools import setup, find_packages
from distutils.command.install import INSTALL_SCHEMES

# to make sure all package data is installed next to the python modules
# see https://groups.google.com/forum/?fromgroups#!topic/comp.lang.python/Nex7L-026uw
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

dependencies = (
    'setuptools',
    'django',
    'django_simple_captcha',
    'django_compressor',
    'south',
    'PIL',
)

setup(
    # GENERAL INFO
    name = 'ecm',
    version = ecm.VERSION,
    description = 'EVE Corp Management is a management and decision-making helper-application for EVE Online.',
    long_description = open('README').read(),
    author = 'Robin Jarry',
    author_email = 'diab@diabeteman.com',
    url = 'http://code.google.com/p/eve-corp-management/',
    download_url = 'http://code.google.com/p/eve-corp-management/downloads/list',
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
        'Topic :: Games/Entertainment',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ),

    # DEPENDENCIES
    requires = dependencies,
    install_requires = dependencies,

    # CONTENTS
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    entry_points = {
        'console_scripts': ('ecm-admin = ecm.admin.cli:run'),
    },
)
