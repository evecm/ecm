'''
This file is part of ICE Security Management

Created on 18 apr. 2010
@author: diabeteman
'''
from ism.core.api import connection
from ism.core.parsers.utils import checkApiVersion, markUpdated

from ism.data.common.models import Outpost

from django.db import transaction

DEBUG = False # DEBUG mode

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(debug=False, cache=False):
    """
    Retrieve all corp assets and calculate the changes.
    
    If there's an error, nothing is written in the database
    """
    global DEBUG
    DEBUG = debug
    
    try:
        api = connection.connect(debug=debug, cache=cache)
        apiOutposts = api.eve.ConquerableStationList()
        checkApiVersion(apiOutposts._meta.version)
        
        currentTime = apiOutposts._meta.currentTime
        cachedUntil = apiOutposts._meta.cachedUntil
        if DEBUG : print "current time : %s" % str(currentTime)
        if DEBUG : print "cached util  : %s" % str(cachedUntil)
        
        if DEBUG : print "parsing api response..."
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
                    
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"
        return "%d outposts parsed" % len(apiOutposts.outposts)
    except:
        transaction.rollback()
        raise
