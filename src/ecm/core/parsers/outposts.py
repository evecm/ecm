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





from ecm.core.parsers.utils import checkApiVersion, markUpdated
from ecm.core.eve import api, db
from ecm.data.common.models import Outpost

from django.db import transaction

import logging
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def update():
    """
    Retrieve all corp assets and calculate the changes.
    
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
        for outpost in apiOutposts.outposts :
            db.updateLocationName(outpost.stationID, 
                                  outpost.solarSystemID, 
                                  outpost.stationTypeID, 
                                  outpost.locationName)
        logger.info("%d outposts parsed", len(apiOutposts.outposts))
        logger.debug("update sucessfull")
        logger.info("outposts updated")
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")
        raise
