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


__date__ = "2011 10 16"
__author__ = "diabeteman"

import logging

import ecm
from django.conf import settings

DICT = {}
LIST = []

#------------------------------------------------------------------------------
class ECMApp(object):
    """
    This is a utility class to describe a django app

    ECM will use the instances of this class to perform various tasks:

      - dependencies between apps
      - creation of objects (without the 'initial_data' django feature)
      - contribution to ECM urls
      - contribution to ECM menus
      - etc.
    """
    def __init__(self, package):
        logger = logging.getLogger(__name__)
        try:
            self.package = package

            package_module = __import__(package, fromlist=['ecm.apps', 'ecm.plugins'])

            # get basic info
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

            # get declared tasks for each app
            try:
                self.tasks = package_module.TASKS
            except AttributeError:
                self.tasks = []

            # get declared UrlPermissions for each app
            try:
                self.permissions = package_module.URL_PERMISSIONS
            except AttributeError:
                self.permissions = []
            
            # get declared SharedData for each app
            try:
                self.shared_data = package_module.SHARED_DATA
            except AttributeError:
                self.shared_data = []

            # get this app declared urls
            try:
                self.urlconf = package + '.urls'
                __import__(self.urlconf, fromlist=[package]).urlpatterns
            except (ImportError, AttributeError):
                self.urlconf = None

            # get this app menu contribution
            try:
                self.menu = package_module.MENUS
                if not type(self.menu) == type([]):
                    raise TypeError("attribute 'MENUS' should be a list")
            except AttributeError:
                self.menu = []

            try:
                self.settings = package_module.SETTINGS
            except AttributeError:
                self.settings = {}

        except:
            logger.exception("")
            raise

    def __str__(self):
        return self.package

#------------------------------------------------------------------------------
# detection of all 'core' apps
for app in settings.ECM_CORE_APPS:
    DICT[app] = ECMApp(package=app)
    LIST.append(DICT[app])
