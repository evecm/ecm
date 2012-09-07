# Copyright (c) 2011 jerome Vacher
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

__date__ = "2012 09 07"
__author__ = "tash"

import logging
import re

from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext as tr

from ecm.plugins.pos.models import POS, FuelLevel
from ecm.apps.eve.models import CelestialObject, ControlTowerResource, Type
from ecm.plugins.pos import constants
from ecm.apps.common import api
from ecm.apps.corp.models import Corporation

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update():
    """
    Stub.
    !!!TODO: Implement
    """
    pass
