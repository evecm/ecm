'''
This file is part of EVE Corporation Management

Created on 23 mar. 2010
@author: diabeteman
'''


from ecm.data.assets.models import DbAsset, DbAssetDiff
from ecm.core.api import connection
from ecm.core.api.connection import API
from ecm.core.parsers import utils
from ecm.core.parsers.assetsconstants import STATIONS_IDS, OFFICE_TYPEID,\
                                      HANGAR_FLAG, BOOKMARK_TYPEID,\
                                      NPC_LOCATION_OFFSET, CONQUERABLE_LOCATION_IDS,\
                                      CONQUERABLE_LOCATION_OFFSET, NPC_LOCATION_IDS
                                      
from django.db import transaction
from ecm import settings

import logging.config

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("parser_assets")

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(cache=False):
    """
    Retrieve all corp assets and calculate the changes.
    
    If there's an error, nothing is written in the database
    """
    try:
        logger.info("fetching /corp/AssetList.xml.aspx...")
        api = connection.connect(cache=cache)
        apiAssets = api.corp.AssetList(characterID=API.CHAR_ID)
        utils.checkApiVersion(apiAssets._meta.version)
        
        currentTime = apiAssets._meta.currentTime
        cachedUntil = apiAssets._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))
        
        logger.debug("fetching old assets from the database...")
        oldItems = {}
        for a in DbAsset.objects.all():
            oldItems[a] = a
        
        newItems = {}
        logger.debug("%d assets fetched", len(oldItems.keys()))
        
        logger.info("parsing api response...")
        for row in apiAssets.assets :
            if row.locationID >= STATIONS_IDS :
                if row.typeID == BOOKMARK_TYPEID :
                    continue # we don't give a flying @#!$ about the bookmarks...
                elif row.typeID == OFFICE_TYPEID :
                    isOffice(office=row, newItems=newItems)
                elif row.flag in HANGAR_FLAG.keys() :
                    isInHangar(item=row, newItems=newItems)
        logger.info("%d assets parsed", len(newItems.keys()))

        diffs = []
        if len(oldItems) != 0 :
            logger.debug("computing diffs since last asset scan...")
            diffs = getAssetDiffs(newItems=newItems, oldItems=oldItems, date=currentTime)
            if diffs:
                for assetDiff in diffs : 
                    assetDiff.save()
                # we store the update time of the table
                utils.markUpdated(model=DbAssetDiff, date=currentTime)
            DbAsset.objects.all().delete()
        for asset in newItems.values() : asset.save()
        
        # we store the update time of the table
        utils.markUpdated(model=DbAsset, date=currentTime)
            
        logger.info("%d changes since last scan", len(diffs))
        logger.debug("saving to database...")
        transaction.commit()
        logger.debug("DATABASE UPDATED!")
        logger.info("assets updated")

    except Exception, e:
        # error catched, rollback changes
        transaction.rollback()
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        logger.error("".join(errortrace))
        raise
    
#------------------------------------------------------------------------------
def getAssetDiffs(oldItems, newItems, date):
    removed, added = utils.calcDiffs(oldItems=oldItems, newItems=newItems)
    __removeDuplicates(removed)
    __removeDuplicates(added)
    
    diffs = []
    
    # so we don't get an Attribute error when calling addasset.duplicate
    for a in added: a.duplicate = False 
    
    for remasset in removed:
        added_qty = 0
        for addasset in added:
            if not addasset.duplicate and addasset.lookslike(remasset):
                # if there is a match (there cannot be more than one), the added asset 
                # was already in the removed assets. We tag the added asset to duplicate 
                # and take it in consideration when creating the "removed" DbAssetDiff
                addasset.duplicate = True
                added_qty = addasset.quantity
                break
        if (added_qty - remasset.quantity): 
            # if the added asset doesn't negates the removed one, we create a diff
            diffs.append(DbAssetDiff(locationID = remasset.locationID,
                                     hangarID = remasset.hangarID,
                                     typeID = remasset.typeID,
                                     quantity = added_qty - remasset.quantity,
                                     date = date,
                                     new = False))
    for addasset in added:
        if not addasset.duplicate:
            diffs.append(DbAssetDiff(locationID = addasset.locationID,
                                     hangarID = addasset.hangarID,
                                     typeID = addasset.typeID,
                                     quantity = addasset.quantity,
                                     date = date,
                                     new = True))
    return diffs

#------------------------------------------------------------------------------
def __removeDuplicates(assetlist):
    assetlist.sort()
    # we sort assets by locationID, hangarID then typeID in order to merge duplicates
    try:
        i = 0
        while(True):
            if assetlist[i].lookslike(assetlist[i + 1]):
                # the assets are sorted so we can merge and delete the duplicate one
                assetlist[i].quantity += assetlist[i + 1].quantity
                del assetlist[i + 1]
            else:
                i += 1
    except IndexError: 
        # when we reach the end of the list we WILL get an IndexError, 
        # this is the only way to stop the loop :-)
        pass

#------------------------------------------------------------------------------
def isOffice(office, newItems):
    try :
        for item in office.contents :
            if item.typeID == BOOKMARK_TYPEID : 
                continue # we don't give a flying @#!$ about the bookmarks...
            isInHangar(item=item, newItems=newItems, locationID=office.locationID)
    except AttributeError :
        pass

#------------------------------------------------------------------------------
def isInHangar(item, newItems, locationID=None):
    asset = assetFromRow(item)
    if locationID : # we come from isOffice() and the item has no locationID attribute
        asset.locationID = locationIDtoStationID(locationID)
    else : # we come from the update() method and the item has a locationID attribute
        asset.locationID = locationIDtoStationID(item.locationID)
    asset.hangarID = HANGAR_FLAG[item.flag]
    newItems[asset] = asset

    try :
        fillContents(container=asset, item=item, newItems=newItems)
        asset.hasContents = True
    except AttributeError :
        pass
    
       
#------------------------------------------------------------------------------
def fillContents(container, item, newItems):
    for _item in item.contents :
        if _item.typeID == BOOKMARK_TYPEID : 
            continue # we don't give a flying @#!$ about the bookmarks...
        _asset = assetFromRow(_item)
        _asset.locationID = container.locationID
        _asset.hangarID = container.hangarID
        _asset.container1 = container.itemID
        newItems[_asset] = _asset
        
        try :
            for __item in _item.contents :
                
                if __item.typeID == BOOKMARK_TYPEID : 
                    continue # we don't give a flying @#!$ about the bookmarks...
                __asset = assetFromRow(__item)
                __asset.locationID = container.locationID
                __asset.hangarID = container.hangarID
                __asset.container1 = container.itemID
                __asset.container2 = _asset.itemID
                newItems[__asset] = __asset
            
            _asset.hasContents = True
        except AttributeError :
            continue
                
        
        
#------------------------------------------------------------------------------
def assetFromRow(row):
    return DbAsset(itemID      = row.itemID,
                   typeID      = row.typeID,
                   quantity    = row.quantity,
                   flag        = row.flag,
                   singleton   = row.singleton)
     
#------------------------------------------------------------------------------
def locationIDtoStationID(locationID):
    """
    to convert locationIDs starting 66 to stationIDs from staStations 
                                                    subtract 6000001 from the locationID
    to convert locationIDs starting 67 to stationIDs from the eveAPI 
                            ConquerableStationList subtract 6000000 from the locationID
    
    source : http://www.eveonline.com/ingameboard.asp?a=topic&threadID=667487
    """
    if locationID <  NPC_LOCATION_IDS :
        return locationID
    elif locationID >= CONQUERABLE_LOCATION_IDS :
        return locationID - CONQUERABLE_LOCATION_OFFSET
    elif locationID >= NPC_LOCATION_IDS :
        return locationID - NPC_LOCATION_OFFSET
    
