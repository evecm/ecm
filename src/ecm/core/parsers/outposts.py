'''
This file is part of EVE Corporation Management

Created on 18 apr. 2010
@author: diabeteman
'''
from ecm.core.api import connection
from ecm.core.parsers.utils import checkApiVersion, markUpdated
from ecm.core import db
from ecm.data.common.models import Outpost
from ecm import settings

from django.db import transaction

import logging.config

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("parser_outposts")

#------------------------------------------------------------------------------
@transaction.commit_manually
def update():
    """
    Retrieve all corp assets and calculate the changes.
    
    If there's an error, nothing is written in the database
    """
    
    try:
        logger.info("fetching /eve/ConquerableStationList.xml.aspx...")
        api = connection.connect()
        apiOutposts = api.eve.ConquerableStationList()
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
        db.invalidateCache()
        logger.debug("DATABASE UPDATED!")
        logger.info("outposts updated")
    except Exception, e:
        # error catched, rollback changes
        transaction.rollback()
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        logger.error("".join(errortrace))
        raise
