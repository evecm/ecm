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

__date__ = "2010-04-08"
__author__ = "diabeteman"

import logging

from django.db import transaction

from ecm.core.eve import api, db
from ecm.core.parsers import checkApiVersion

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success(using='eve')
def update():
    """
    Retrieve all corp owned stations and update their name in the EVE database.
    Creating new entries if needed.
    
    If there's an error, nothing is written in the database
    """
    try:
        logger.info("fetching /eve/ConquerableStationList.xml.aspx...")
        api_conn = api.connect()
        apiOutposts = api_conn.eve.ConquerableStationList()
        checkApiVersion(apiOutposts._meta.version)
        
        currentTime = apiOutposts._meta.currentTime
        cachedUntil = apiOutposts._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))
        
        logger.debug("parsing api response...")
        created = 0
        updated = 0
        for outpost in apiOutposts.outposts :
            if db.updateLocationName(stationID=outpost.stationID, 
                                     solarSystemID=outpost.solarSystemID, 
                                     locationName=outpost.stationName):
                created += 1
            else:
                updated += 1
        logger.info("%d new outposts, %d updated", created, updated)
        logger.debug("update sucessfull")
        logger.info("outposts updated")
    except:
        # error catched, rollback changes
        logger.exception("update failed")
        raise
