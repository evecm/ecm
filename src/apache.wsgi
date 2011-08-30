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

# I modified the WSGI initialization script according to this post:
# http://blog.dscpl.com.au/2010/03/improved-wsgi-script-for-use-with.html
# which I found very interesting and pertinent.

import sys
from os import path

install_dir = path.abspath(path.dirname(__file__))
sys.path.insert(0, path.join(install_dir, 'ecm'))

# this import should be marked as not found when analysing this module 
# with the eclipse python editor.
# This is normal, as the 'ecm' folder is not in sys.path when performing
# a static analysis.
import settings 

from django.core import management

management.setup_environ(settings)
utility = management.ManagementUtility()
command = utility.fetch_command('runserver')
command.validate()

import django.conf.settings
from django.utils import translation
translation.activate(django.conf.settings.LANGUAGE_CODE)

from django.core.handlers import wsgi

application = wsgi.WSGIHandler()
