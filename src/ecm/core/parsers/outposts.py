# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-04-08"
__author__ = "diabeteman"





from ecm.core import api
from ecm.core.parsers.utils import checkApiVersion, markUpdated
from ecm.core import evedb
from ecm.data.common.models import Outpost

from django.db import transaction

import logging
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_manually
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
        Outpost.objects.all().delete()
        for outpost in apiOutposts.outposts :
            Outpost(stationID=outpost.stationID,
                    stationName=outpost.stationName,
                    stationTypeID=outpost.stationTypeID,
                    solarSystemID=outpost.solarSystemID,
                    corporationID=outpost.corporationID,
                    corporationName=outpost.corporationName).save()
        # we store the update time of the table
        markUpdated(model=Outpost, date=currentTime)
                    
        logger.info("%d outposts parsed", len(apiOutposts.outposts))
        logger.debug("saving data to the database...")
        transaction.commit()
        evedb.invalidateCache()
        logger.debug("update sucessfull")
        logger.info("outposts updated")
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")
        raise
