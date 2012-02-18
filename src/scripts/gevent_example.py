#!/bin/env python
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

"""
This script allows to run ECM into gevent WSGI server. 
See http://code.google.com/p/eve-corp-management/wiki/InstallationInstructions#Deployment_alternatives_(standalone_WSGI_server_behind_a_reverse
for more information.
"""

__date__ = "2012-02-18"
__author__ = "diabeteman"

import sys
from os import path

install_dir = path.abspath(path.join(path.abspath(path.dirname(__file__)), '..'))
sys.path.insert(0, path.join(install_dir, 'ecm'))

# this import should be marked as not found when analysing this module 
# with the eclipse python editor.
# This is normal, as the 'ecm' folder is not in sys.path when performing
# a static analysis.
import settings #@UnresolvedImport

from django.core import management

management.setup_environ(settings)
utility = management.ManagementUtility()
command = utility.fetch_command('runserver')
command.validate()

from django.conf import settings as django_settings
from django.utils import translation
translation.activate(django_settings.LANGUAGE_CODE)

import django.core.handlers.wsgi

from gevent.pywsgi import WSGIServer


if __name__ == '__main__':
    bind_address = '127.0.0.1', 8000
    application = django.core.handlers.wsgi.WSGIHandler()
    server = WSGIServer(bind_address, application)
    try:
        print 'Running ECM server on %s:%d' % bind_address
        print 'Hit CTRL + C to stop'
        server.serve_forever()
    except KeyboardInterrupt:
        server.stop()

