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

from distutils.version import LooseVersion

import ecm
import ecm.apps
from ecm.apps import ECMApp
from django.conf import settings


settings
ECM_VERSION = LooseVersion(ecm.VERSION)

DICT = {}
LIST = []


LOGGER = logging.getLogger(__name__)

# detection of all 'plugins' apps
for app in settings.ECM_PLUGIN_APPS:
    DICT[app] = ECMApp(package=app)
    LIST.append(DICT[app])

for app in LIST:
    for req_name, min_version in app.dependencies.items():
        dependency_problem = False
        min_version = LooseVersion(min_version)
        actual_version = None
        if req_name == 'ecm':
            actual_version = ECM_VERSION
            dependency_problem = ECM_VERSION < min_version
        else:
            dependency = DICT.get(req_name, None)
            if dependency is None:
                dependency = ecm.apps.DICT.get(req_name, None)
            if dependency is None:
                dependency_problem = True
            else:
                actual_version = dependency.version
                dependency_problem = LooseVersion(dependency.version) < min_version
        if dependency_problem:
            LOGGER.warning('Plugin "%s" requires "%s" version %s or later (found %s)'
                            % (app.package, req_name, min_version, actual_version))
