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

__date__ = "2010-04-08"
__author__ = "diabeteman"

import logging

from django.db import transaction

from ecm.apps.eve.models import CelestialObject
from ecm.apps.common import api
from ecm.apps.eve import constants

LOG = logging.getLogger(__name__)
#------------------------------------------------------------------------------
@transaction.commit_on_success()
def update():
    """
    Retrieve all corp owned stations and update their name in the EVE database.
    Creating new entries if needed.

    If there's an error, nothing is written in the database
    """

    LOG.info("fetching /eve/ConquerableStationList.xml.aspx...")
    api_conn = api.connect()
    apiOutposts = api_conn.eve.ConquerableStationList()
    api.check_version(apiOutposts._meta.version)
    created = 0
    updated = 0
    for outpost in apiOutposts.outposts:
        try:
            station = CelestialObject.objects.get(itemID=outpost.stationID)
            if station.itemName != outpost.stationName:
                station.itemName = outpost.stationName
            updated += 1
        except CelestialObject.DoesNotExist:
            system = CelestialObject.objects.get(itemID = outpost.solarSystemID)
            station = CelestialObject(itemID=outpost.stationID,
                                      type_id=outpost.stationTypeID,
                                      groupID=constants.STATIONS_GROUPID,
                                      solarSystemID=outpost.solarSystemID,
                                      regionID=system.regionID,
                                      itemName=outpost.stationName,
                                      security=system.security)
            created += 1
        station.save()
    LOG.info("%d new outposts, %d updated", created, updated)
