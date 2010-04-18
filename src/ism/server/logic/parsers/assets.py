'''
This file is part of ICE Security Management

Created on 23 mar. 2010
@author: diabeteman
'''


from ism.server.data.assets.models import DbAsset, DbAssetDiff
from ism.server.logic.api import connection
from ism.server.logic.api.connection import API
from django.db import transaction
from ism.server.logic.parsers.utils import checkApiVersion
from ism.server.logic.assets.constants import STATIONS_IDS, DELIVERIES_FLAG, OFFICE_TYPEID,\
                                              HANGAR_FLAG, DELIVERIES_HANGAR_ID, BOOKMARK_TYPEID

from datetime import datetime

DEBUG = False # DEBUG mode

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(debug=False):
    """
    Retrieve all corp assets and calculate the changes.
    
    If there's an error, nothing is written in the database
    """
    global DEBUG
    DEBUG = debug
    
    try:
        api = connection.connect(debug=debug)
        apiAssets = api.corp.AssetList(characterID=API.CHAR_ID)
        checkApiVersion(apiAssets._meta.version)
        
        currentTime = apiAssets._meta.currentTime
        cachedUntil = apiAssets._meta.cachedUntil
        if DEBUG : print "current time : %s" % str(datetime.fromtimestamp(currentTime))
        if DEBUG : print "cached util  : %s" % str(datetime.fromtimestamp(cachedUntil))
        
        newList = []
        
        if DEBUG : print "fetching old assets from the database..."
        oldList = list(DbAsset.objects.all())
        
        if DEBUG : print "parsing api response..."
        for row in apiAssets.assets :
            if row.locationID >= STATIONS_IDS :
                if row.typeID == BOOKMARK_TYPEID :
                    continue # we don't give a flying @#!$ about the bookmarks...
                elif row.flag == DELIVERIES_FLAG :
                    isInDeliveries(item=row, assetList=newList)
                elif row.typeID == OFFICE_TYPEID :
                    isOffice(office=row, assetList=newList)
                elif row.flag in HANGAR_FLAG.keys() :
                    isInHangar(item=row, assetList=newList)
        
        if len(oldList) != 0 :
            if DEBUG : print "computing diffs since last asset scan..."
            diffs = getAssetDiffs(newList, oldList, date=currentTime)
            if diffs :
                if DEBUG : print "saving changes to the database..."
                for assetDiff in diffs : assetDiff.save()
                DbAsset.objects.all().delete()
                for asset in newList : asset.save()
            # if no diff, we do nothing
        else :
            # 1st import, no diff to write
            if DEBUG : print "saving data to the database..."
            for asset in newList : asset.save()
            
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"
    except:
        transaction.rollback()
        raise
    
#------------------------------------------------------------------------------
def getAssetDiffs(newList, oldList, date):
    removed  = [ a for a in oldList if a not in newList ]
    added    = [ a for a in newList if a not in oldList ]
    
    diffs    = []
    if DEBUG:
        print "REMOVED ASSETS:"
        if not removed : print "(none)"
        else : print "  %9s %7s %7s %10s" % ("station","hangar","item","quantity")
    for remasset in removed:
        if DEBUG: print "- " + repr(remasset)
        diffs.append(DbAssetDiff(locationID = remasset.locationID,
                                 hangarID = remasset.hangarID,
                                 typeID = remasset.typeID,
                                 quantity = remasset.quantity,
                                 date = date,
                                 new = False))
    if DEBUG:
        print "ADDED ASSETS:"
        if not added : print "(none)"
        else : print "  %9s %7s %7s %10s" % ("station","hangar","item","quantity")
    for addasset in added:
        if DEBUG: print "+ " + repr(addasset)
        diffs.append(DbAssetDiff(locationID = addasset.locationID,
                                 hangarID = addasset.hangarID,
                                 typeID = addasset.typeID,
                                 quantity = addasset.quantity,
                                 date = date,
                                 new = True))
        
    return diffs
    
#------------------------------------------------------------------------------
def isInDeliveries(item, assetList):
    if item.typeID == BOOKMARK_TYPEID : 
        return # we don't give a flying @#!$ about the bookmarks...
    asset = assetFromRow(item)
    asset.locationID = item.locationID
    asset.hangarID = DELIVERIES_HANGAR_ID
    try :
        fillContents(container=asset, item=item, assetList=assetList)
        asset.hasContents = True
    except AttributeError :
        pass
    
    assetList.append(asset)

#------------------------------------------------------------------------------
def isOffice(office, assetList):
    if hasContents(office) :
        for item in office.contents :
            if item.typeID == BOOKMARK_TYPEID : 
                continue # we don't give a flying @#!$ about the bookmarks...
            isInHangar(item=item, assetList=assetList, locationID=office.locationID)

#------------------------------------------------------------------------------
def isInHangar(item, assetList, locationID=None):
    asset = assetFromRow(item)
    if locationID : # we come from isOffice() and the item has no locationID attribute
        asset.locationID = locationID
    else : # we come from the update() method and the item has a locationID attribute
        asset.locationID = item.locationID
    asset.hangarID = HANGAR_FLAG[item.flag]
    try :
        fillContents(container=asset, item=item, assetList=assetList)
        asset.hasContents = True
    except AttributeError :
        pass
    
    assetList.append(asset)
       
#------------------------------------------------------------------------------
def fillContents(container, item, assetList):
    for _item in item.contents :
        if _item.typeID == BOOKMARK_TYPEID : 
            continue # we don't give a flying @#!$ about the bookmarks...
        _asset = assetFromRow(_item)
        _asset.locationID = container.locationID
        _asset.hangarID = container.hangarID
        _asset.container1 = container.itemID
        
        try :
            for __item in _item.contents :
                
                if __item.typeID == BOOKMARK_TYPEID : 
                    continue # we don't give a flying @#!$ about the bookmarks...
                __asset = assetFromRow(__item)
                __asset.locationID = container.locationID
                __asset.hangarID = container.hangarID
                __asset.container1 = container.itemID
                __asset.container2 = _asset.itemID
                assetList.append(__asset)
            
            _asset.hasContents = True
        except AttributeError :
            continue
                
        assetList.append(_asset)
        
        
#------------------------------------------------------------------------------
def assetFromRow(row):
    return DbAsset(itemID      = row.itemID,
                   typeID      = row.typeID,
                   quantity    = row.quantity,
                   flag        = row.flag,
                   singleton   = row.singleton)
     
#------------------------------------------------------------------------------
def hasContents(row):
    return len(row._cols) == len(row._row)
    
