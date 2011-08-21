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

__date__ = "2010-03-23"
__author__ = "diabeteman"

import logging

from django.db import transaction

from ecm.data.assets.models import Asset, AssetDiff
from ecm.core.eve import api, db
from ecm.core.eve import constants as cst
from ecm.core.parsers import calcDiffs, markUpdated, checkApiVersion

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_manually
def update():
    """
    Retrieve all corp assets and calculate the changes.
    
    If there's an error, nothing is written in the database
    """
    try:
        logger.info("fetching /corp/AssetList.xml.aspx...")
        api_conn = api.connect()
        apiAssets = api_conn.corp.AssetList(characterID=api.get_api().charID)
        checkApiVersion(apiAssets._meta.version)
        
        currentTime = apiAssets._meta.currentTime
        cachedUntil = apiAssets._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))
        
        logger.debug("fetching old assets from the database...")
        oldItems = {}
        for a in Asset.objects.all():
            oldItems[a] = a
        
        newItems = {}
        logger.debug("%d assets fetched", len(oldItems.keys()))
        
        logger.info("parsing api response...")
        for row in apiAssets.assets:
            if row.typeID == cst.BOOKMARK_TYPEID:
                continue # we don't give a flying @#!$ about the bookmarks...
            
            if row.locationID >= cst.STATIONS_IDS:
                # this row contains assets in a station
                if row.typeID == cst.OFFICE_TYPEID:
                    rowIsOffice(office=row, items_dic=newItems)
                else:
                    rowIsInHangar(item=row, items_dic=newItems)
            else:
                # this row contains assets in space
                try:
                    if cst.HAS_HANGAR_DIVISIONS[row.typeID]:
                        rowIsPOSCorporateHangarArray(corpArray=row, items_dic=newItems)
                    else:
                        rowIsPOSArray(array=row, items_dic=newItems)
                except KeyError:
                    # unhandled typeID, this may be a reactor array or some other crap
                    pass
        
        logger.info("%d assets parsed", len(newItems))

        diffs = []
        if len(oldItems) != 0:
            logger.debug("computing diffs since last asset scan...")
            diffs = getAssetDiffs(newItems=newItems, oldItems=oldItems, date=currentTime)
            if diffs:
                for assetDiff in diffs: 
                    assetDiff.save()
                # we store the update time of the table
                markUpdated(model=AssetDiff, date=currentTime)
            Asset.objects.all().delete()
        for asset in newItems.values(): 
            asset.save()
        
        # we store the update time of the table
        markUpdated(model=Asset, date=currentTime)
            
        logger.info("%d changes since last scan", len(diffs))
        logger.debug("saving to database...")
        transaction.commit()
        logger.debug("DATABASE UPDATED!")
        logger.info("assets updated")
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")
        raise
    
#------------------------------------------------------------------------------
def getAssetDiffs(oldItems, newItems, date):
    removed, added = calcDiffs(oldItems=oldItems, newItems=newItems)
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
                # and take it in consideration when creating the "removed" AssetDiff
                addasset.duplicate = True
                added_qty = addasset.quantity
                break
        if (added_qty - remasset.quantity): 
            # if the added asset doesn't negates the removed one, we create a diff
            diffs.append(AssetDiff(solarSystemID = remasset.solarSystemID,
                                       stationID = remasset.stationID,
                                        hangarID = remasset.hangarID,
                                          typeID = remasset.typeID,
                                            flag = remasset.flag,
                                        quantity = added_qty - remasset.quantity,
                                            date = date,
                                             new = False))
    for addasset in added:
        if not addasset.duplicate:
            diffs.append(AssetDiff(solarSystemID = addasset.solarSystemID,
                                       stationID = addasset.stationID,
                                        hangarID = addasset.hangarID,
                                          typeID = addasset.typeID,
                                            flag = addasset.flag,
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
def rowIsOffice(office, items_dic):
    """
    'office' represents an office in a station
    
    The 'stationID' of all the contents of the array is encoded from the 'itemID' 
    and the 'typeID' of the row.
    """
    try :
        stationID = locationIDtoStationID(office.locationID)
        solarSystemID = db.getSolarSystemID(stationID)
        for item in office.contents:
            if item.typeID == cst.BOOKMARK_TYPEID : 
                continue # we don't give a flying @#!$ about the bookmarks...
            rowIsInHangar(item=item, items_dic=items_dic, 
                       solarSystemID=solarSystemID, stationID=stationID)
    except AttributeError:
        # skip the office if it has no contents
        pass

#------------------------------------------------------------------------------
def rowIsPOSCorporateHangarArray(corpArray, items_dic):
    """
    'corpArray' represents an anchorable structure with corporate hangar divisions
    such as a 'Corporate Hangar Array' or a 'Mobile Laboratory'
    
    The 'stationID' of all the contents of the array is encoded from the 'itemID' 
    and the 'typeID' of the row.
    """
    try:
        solarSystemID = corpArray.locationID
        stationID = corpArray.itemID
        flag = corpArray.typeID 
        for item in corpArray.contents:
            if item.typeID == cst.BOOKMARK_TYPEID : 
                continue # we don't give a flying @#!$ about the bookmarks...
            rowIsInHangar(item=item, 
                          items_dic=items_dic, 
                          solarSystemID=solarSystemID, 
                          stationID=stationID,
                          flag=flag)
    except AttributeError:
        # skip the corpArray if it has no contents
        pass

#------------------------------------------------------------------------------
def rowIsPOSArray(array, items_dic):
    """
    'array' represents an anchorable structure with no corporate hangar divisions
    such as a 'Ship Maintenance Array' or a 'Silo'
    
    The 'stationID' is encoded the same way than in rowIsPOSCorporateHangarArray()
    but we force the 'hangarID' of all contained items to '0' (no corporate divisions)
    """
    try :
        solarSystemID = array.locationID
        stationID = array.itemID
        flag = array.typeID 
        for item in array.contents:
            if item.typeID == cst.BOOKMARK_TYPEID : 
                continue # we don't give a flying @#!$ about the bookmarks...
            rowIsInHangar(item=item, 
                          items_dic=items_dic, 
                          solarSystemID=solarSystemID, 
                          stationID=stationID, 
                          hangarID=0,
                          flag=flag)
    except AttributeError:
        # if the array has no attribute 'contents', we ignore it
        pass
       
#------------------------------------------------------------------------------
def rowIsInHangar(item, items_dic, solarSystemID=None, stationID=None, hangarID=None, flag=None):
    """
    'item' represents an asset located in a hangar division.
    """
    asset = assetFromRow(item)
    
    if solarSystemID is None and stationID is None:
        # we come from the update() method and the item has a locationID attribute
        asset.stationID = locationIDtoStationID(item.locationID)
        asset.solarSystemID = db.getSolarSystemID(asset.stationID)
    else: 
        asset.solarSystemID = solarSystemID
        asset.stationID = stationID
    
    if hangarID is None:
        try:
            asset.hangarID = cst.HANGAR_FLAG[item.flag]
        except KeyError:
            # if unhandled flag (i.e. not a hangar division)
            # allways fall back to the first division 
            asset.hangarID = 1000
    else:
        asset.hangarID = hangarID
    
    if flag is not None:
        asset.flag = flag

    items_dic[asset] = asset
    
    try:
        fillContents(container=asset, item=item, items_dic=items_dic, flag=flag)
        asset.hasContents = True
    except AttributeError:
        # if the item has no attribute 'contents', we're done
        pass

#------------------------------------------------------------------------------
def fillContents(container, item, items_dic, flag=None):
    """
    Try to fill the contents of an item (assembled ship, assembled container)
    If the item has no contents, raise an attribute error. 
    """
    for _item in item.contents:
        if _item.typeID == cst.BOOKMARK_TYPEID: 
            continue # we don't give a flying @#!$ about the bookmarks...
        _asset = assetFromRow(_item)
        _asset.solarSystemID = container.solarSystemID
        _asset.stationID = container.stationID
        _asset.hangarID = container.hangarID
        _asset.container1 = container.itemID
        if flag is not None:
            _asset.flag = flag
        items_dic[_asset] = _asset
        
        try :
            for __item in _item.contents:
                if __item.typeID == cst.BOOKMARK_TYPEID: 
                    continue # we don't give a flying @#!$ about the bookmarks...
                __asset = assetFromRow(__item)
                __asset.solarSystemID = container.solarSystemID
                __asset.stationID = container.stationID
                __asset.hangarID = container.hangarID
                __asset.container1 = container.itemID
                __asset.container2 = _asset.itemID
                if flag is not None:
                    __asset.flag = flag
                items_dic[__asset] = __asset
            
            _asset.hasContents = True
        except AttributeError:
            # if '__item' has no attribute 'contents', we're skip to the next one
            continue
                
        
        
#------------------------------------------------------------------------------
def assetFromRow(row):
    return Asset(itemID    = row.itemID,
                 typeID    = row.typeID,
                 quantity  = row.quantity,
                 flag      = row.flag,
                 singleton = row.singleton)
     
#------------------------------------------------------------------------------
def locationIDtoStationID(locationID):
    """
    to convert locationIDs starting 66000000 to stationIDs from staStations 
                                                    subtract 6000001 from the locationID
    to convert locationIDs starting 66014933 to stationIDs from the eveAPI 
                            ConquerableStationList subtract 6000000 from the locationID
    
    source : http://www.eveonline.com/ingameboard.asp?a=topic&threadID=667487
    """
    if locationID < 66000000:
        return locationID
    elif locationID < 66014933:
        return locationID - 6000001
    else:
        return locationID - 6000000
    
