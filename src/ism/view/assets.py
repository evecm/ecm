'''
This file is part of ICE Security Management

Created on 21 mai 2010
@author: diabeteman
'''
import json

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

from ism.core import db
from ism.data.common.models import UpdateDate
from ism.data.assets.models import DbAsset
from ism.data.corp.models import Hangar

SQL_STATIONS = "SELECT itemID, locationID, count(*) AS items FROM assets_dbasset GROUP BY locationID;"
SQL_HANGARS = "SELECT itemID, hangarID, count(*) AS items FROM assets_dbasset WHERE locationID=%d GROUP BY hangarID ORDER BY hangarID;"


HANGAR = {}
for h in Hangar.objects.all():
    HANGAR[h.hangarID] = h.name
    
CATEGORY_ICONS = { 2 : "can" , 
                   4 : "mineral" , 
                   6 : "ship" , 
                   8 : "ammo" , 
                   9 : "blueprint",
                  16 : "skill" }

#------------------------------------------------------------------------------
@login_required
@cache_page(60 * 15) # 15 minutes cache
def stations(request):
    data = {  'station_list' : getStations(),
                'item_count' : getItemCount(),
                 'scan_date' : getScanDate() }
    return render_to_response("assets.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@login_required
@cache_page(60 * 15) # 15 minutes cache
def hangars(request, stationID):
    json_data = json.dumps(getStationHangars(int(stationID)))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@login_required
@cache_page(60 * 15) # 15 minutes cache
def hangar_contents(request, stationID, hangarID):
    json_data = json.dumps(getHangarContents(int(stationID), int(hangarID)))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@login_required
@cache_page(60 * 15) # 15 minutes cache
def can1_contents(request, stationID, hangarID, container1):
    json_data = json.dumps(getCan1Contents(int(stationID), int(hangarID), int(container1)))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@login_required
@cache_page(60 * 15) # 15 minutes cache
def can2_contents(request, stationID, hangarID, container1, container2):
    json_data = json.dumps(getCan2Contents(int(stationID), int(hangarID), int(container1), int(container2)))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@login_required
@cache_page(60 * 15) # 15 minutes cache
def search_items(request):
    json_data = json.dumps(search(request.GET.get("search_string", "no-item")))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
def getStations():
    raw_list = DbAsset.objects.raw(SQL_STATIONS)
    class S: 
        locationID = 0
        name = None
        items = 0
    station_list = []
    for s in raw_list:
        station = S()
        station.locationID = s.locationID
        station.name = db.resolveLocationName(s.locationID)
        station.items = s.items
        station_list.append(station)
    return station_list

#------------------------------------------------------------------------------
def getItemCount():
    return len(DbAsset.objects.all())

#------------------------------------------------------------------------------
def getStationHangars(stationID):
    raw_list = DbAsset.objects.raw(SQL_HANGARS % stationID)
    hangar_list = []
    for h in raw_list:
        hangar = {}
        hangar["data"] = '<b>%s</b><i> - (%d items)</i>' % (HANGAR[h.hangarID], h.items)
        id = "%d_%d_" % (stationID, h.hangarID) 
        hangar["attr"] = { "id" : id , "rel" : "hangar" , "href" : "" , "class" : "hangar-row" }
        hangar["state"] = "closed"
        hangar_list.append(hangar)
    
    return hangar_list
#------------------------------------------------------------------------------
def getHangarContents(stationID, hangarID):
    item_list = DbAsset.objects.filter(locationID=stationID, hangarID=hangarID, 
                                       container1=None, container2=None)
    json_data = []
    for i in item_list:
        item = {}
        name, category = db.resolveTypeName(i.typeID)
        try:    icon = CATEGORY_ICONS[category]
        except: icon = "item"
        
        if i.hasContents:
            item["data"] = "%s" % name
            id = "%d_%d_%d_" % (stationID, hangarID, i.itemID)
            item["attr"] = { "id" : id , "rel" : icon , "href" : "" }
            item["state"] = "closed"
        elif i.singleton:
            item["data"] = name
            item["attr"] = { "rel" : icon , "href" : ""  }
        else:
            item["data"] = "%s <i>- (x %d)</i>" % (name, i.quantity)
            item["attr"] = { "rel" : icon , "href" : "" }
        json_data.append(item)
        
    return json_data

#------------------------------------------------------------------------------
def getCan1Contents(stationID, hangarID, container1):
    item_list = DbAsset.objects.filter(locationID=stationID, hangarID=hangarID, 
                                       container1=container1, container2=None)
    json_data = []
    for i in item_list:
        item = {}
        name, category = db.resolveTypeName(i.typeID)
        try:    icon = CATEGORY_ICONS[category]
        except: icon = "item"
        
        if i.hasContents:
            item["data"] = name
            id = "%d_%d_%d_%d_" % (stationID, hangarID, container1, i.itemID)
            item["attr"] = { "id" : id , "rel" : icon , "href" : "", "class" : "%s-row" % icon  }
            item["state"] = "closed"
        elif i.singleton:
            item["data"] = name
            item["attr"] = { "rel" : icon , "href" : ""  }
        else:
            item["data"] = "%s <i>- (x %d)</i>" % (name, i.quantity)
            item["attr"] = { "rel" : icon , "href" : ""  }
            
        json_data.append(item)
        
    return json_data

#------------------------------------------------------------------------------
def getCan2Contents(stationID, hangarID, container1, container2):
    item_list = DbAsset.objects.filter(locationID=stationID, hangarID=hangarID, 
                                       container1=container1, container2=container2)
    json_data = []
    for i in item_list:
        item = {}
        name, category = db.resolveTypeName(i.typeID)
        try:    icon = CATEGORY_ICONS[category]
        except: icon = "item"
        if i.singleton: item["data"] = name
        else:           item["data"] = "%s <i>- (x %d)</i>" % (name, i.quantity)
        item["attr"] = { "rel" : icon , "href" : ""  }
        json_data.append(item)
        
    return json_data

#------------------------------------------------------------------------------  
def search(searchStr):
    matchingIDs = db.getMatchingIdsFromString(searchStr)
    matching_items = DbAsset.objects.filter(typeID__in=matchingIDs)

    json_data = []

    for i in matching_items:
        nodeid = "#%d_" % i.locationID
        json_data.append(nodeid)
        nodeid = nodeid + "%d_" % i.hangarID
        json_data.append(nodeid)
        if i.container1:
            nodeid = nodeid + "%d_" % i.container1
            json_data.append(nodeid)
            if i.container2:
                nodeid = nodeid + "%d_" % i.container2
                json_data.append(nodeid)

    return json_data
#------------------------------------------------------------------------------  
def getScanDate():
    date = UpdateDate.objects.get(model_name=DbAsset.__name__) 
    return date.update_date
#------------------------------------------------------------------------------
