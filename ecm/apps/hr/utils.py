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

__author__ = 'Ajurna'
__date__ = "2013 8 08"

import logging

from django.db import transaction

from ecm.apps.hr.models import Member
from ecm.apps.common import api
from ecm.apps.corp.models import Corporation
from ecm.apps.corp.utils import get_corp

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def get_char(characterID):
    api_conn = api.eveapi.EVEAPIConnection()
    char = api_conn.eve.CharacterInfo(characterID = characterID)
    try:
        corp = Corporation.objects.get(corporationID = char.corporationID)
    except Corporation.DoesNotExist:
        corp = get_corp(char.corporationID)
    LOG.info("Adding new Player: "+ char.characterName)
    mem = Member()
    mem.characterID = char.characterID
    mem.name = char.characterName
    mem.race = char.race
    mem.bloodline = char.bloodline
    mem.corp = corp
    mem.corpDate = char.corporationDate
    mem.securityStatus = char.securityStatus
    mem.save()
    return mem