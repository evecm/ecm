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


from setuptools import setup, find_packages
setup( 
    name='Eve Corporation Management',
    version='2.0.0-HG',
    description='ECM is a web application dedicated to managing corporation in the MMO EVE Online',
    author='Robin Jarry',
    author_email='diabeteman@gmail.com',
    url='http://code.google.com/p/eve-corp-management/',
    download_url='http://code.google.com/p/eve-corp-management/downloads/list',
    license='GPLv3',
    packages=find_packages(),
    install_requires=['setuptools',
                      'PIL',
                      'south',
                      'django-simple-captcha',
                      'django_compressor'],
    

    package_data= {
                'ecm': ['static/ecm/css/*.css',
                        'static/ecm/img/*.*',
                        'static/ecm/img/datatables/*.png',
                        'static/ecm/img/jquery_ui/*.png',
                        'static/ecm/js/*.js',
                        'static/ecm/js/lib/*.*']
                   
                   },
            
    zip_safe = False,
    entry_points = {
                'console_scripts': ['ecm-admin = ecm.admin.main:run']
                 }

    )