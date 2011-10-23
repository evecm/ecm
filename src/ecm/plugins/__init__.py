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


__date__ = "2011 10 16"
__author__ = "diabeteman"


import logging
import ecm
from ecm.settings import ECM_PLUGIN_APPS

LOG = logging.getLogger(__name__)
DICT = {}
LIST = []

class ECMPlugin(object):

    def __init__(self, package):
        try:
            LOG.info("Importing plugin '%s'..." % package)
            self.package = package
            package_module = __import__(package)
            
            try:
                self.version = package_module.VERSION
            except AttributeError:  
                self.version = ecm.VERSION
            try:
                self.dependencies = package_module.DEPENDS_ON
            except AttributeError:  
                self.dependencies = {}
            try:
                self.app_prefix = package_module.NAME
            except AttributeError:  
                self.app_prefix = package.rsplit('.', 1)[-1]
            
            try:
                self.urlconf = package + '.urls'
                __import__(self.urlconf, fromlist=[package]).urlpatterns
            except (ImportError, AttributeError), e:
                LOG.warning(e)
                self.urlconf = None
            try:
                self.menu = __import__(package + '.menu', fromlist=[package]).ECM_MENUS
            except (ImportError, AttributeError), e:
                LOG.warning(e)
                self.menu = []
            LOG.debug('app_prefix: %s', self.app_prefix)
            LOG.debug('version: %s', self.version)
            LOG.debug('depends on: %s', self.dependencies)
            LOG.debug('urlconf: %s', self.urlconf)
            LOG.debug('menus: %s', self.menu)
        except:
            LOG.exception("")
            raise
            

for app in ECM_PLUGIN_APPS:
    DICT[app] = ECMPlugin(package=app)
    LIST.append(DICT[app])
