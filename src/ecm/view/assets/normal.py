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

__date__ = "2011-05-21"
__author__ = "diabeteman"



import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import pluralize
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

from ecm.core import db, utils
from ecm.data.assets.models import DbAsset
from ecm.data.corp.models import Hangar
from ecm.view import getScanDate
from ecm.core.auth import user_is_director

SQL_STATIONS = "SELECT itemID, locationID, count(*) AS items FROM assets_dbasset GROUP BY locationID;"
SQL_STATIONS_FILTERED = "SELECT itemID, locationID, count(*) AS items FROM assets_dbasset WHERE hangarID in %s GROUP BY locationID;"
SQL_HANGARS = "SELECT itemID, hangarID, count(*) AS items FROM assets_dbasset WHERE locationID=%d GROUP BY hangarID ORDER BY hangarID;"
SQL_HANGARS_FILTERED = "SELECT itemID, hangarID, count(*) AS items FROM assets_dbasset WHERE locationID=%d AND hangarID in %s GROUP BY hangarID ORDER BY hangarID;"

CATEGORY_ICONS = { 2 : "can" , 
                   4 : "mineral" , 
                   6 : "ship" , 
                   8 : "ammo" , 
                   9 : "blueprint",
                  16 : "skill" }

#------------------------------------------------------------------------------
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@user_is_director()
def stations(request):
    
    all_hangars = Hangar.objects.all()
    try: 
        divisions_str = request.GET["divisions"]
        divisions = [ int(div) for div in divisions_str.split(",") ]
        for h in all_hangars: h.checked = (h.hangarID in divisions)
    except: 
        divisions, divisions_str = None, None
        for h in all_hangars: h.checked = False
    
    stations = getStations(divisions)
    data = {  'station_list' : stations,
                 'divisions' : divisions, # divisions to show
             'divisions_str' : divisions_str,
                   'hangars' : all_hangars,
                 'scan_date' : getScanDate(DbAsset.__name__) }
    if stations:
        return render_to_response("assets/assets.html", data, context_instance=RequestContext(request))
    else:
        return render_to_response("assets/assets_no_data.html", context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@user_is_director()
def hangars(request, stationID):
    
    try: divisions = [ int(div) for div in request.GET["divisions"].split(",") ]
    except: divisions = None
    
    json_data = json.dumps(getStationHangars(int(stationID), divisions))
    
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@user_is_director()
def hangar_contents(request, stationID, hangarID):
    json_data = json.dumps(getHangarContents(int(stationID), int(hangarID)))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@user_is_director()
def can1_contents(request, stationID, hangarID, container1):
    json_data = json.dumps(getCan1Contents(int(stationID), int(hangarID), int(container1)))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@user_is_director()
def can2_contents(request, stationID, hangarID, container1, container2):
    json_data = json.dumps(getCan2Contents(int(stationID), int(hangarID), int(container1), int(container2)))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@user_is_director()
def search_items(request):
    
    try: divisions = tuple([ int(div) for div in request.GET["divisions"].split(",") ])
    except: divisions = None
    
    search_string = request.GET.get("search_string", "no-item")
    
    json_data = json.dumps(search(search_string, divisions))
    
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
def getStations(divisions):
    if divisions:
        str_divisions = str(divisions).replace("[", "(").replace("]", ")")
        raw_list = DbAsset.objects.raw(SQL_STATIONS_FILTERED % str_divisions)
    else:
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
def getStationHangars(stationID, divisions):
    if divisions:
        str_divisions = str(divisions).replace("[", "(").replace("]", ")")
        sql = SQL_HANGARS_FILTERED % (stationID, str_divisions)
        raw_list = DbAsset.objects.raw(sql)
    else:
        raw_list = DbAsset.objects.raw(SQL_HANGARS % stationID)
    
    HANGAR = {}
    for h in Hangar.objects.all():
        HANGAR[h.hangarID] = h.name
    
    hangar_list = []
    for h in raw_list:
        hangar = {}
        hangar["data"] = '<b>%s</b><i> - (%d item%s)</i>' % (HANGAR[h.hangarID], h.items, pluralize(h.items))
        id = "_%d_%d" % (stationID, h.hangarID) 
        hangar["attr"] = { "id" : id , "rel" : "hangar" , "href" : "" }
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
            item["data"] = name
            id = "_%d_%d_%d" % (stationID, hangarID, i.itemID)
            item["attr"] = { "id" : id , "rel" : icon , "href" : "" }
            item["state"] = "closed"
        elif i.singleton:
            item["data"] = name
            item["attr"] = { "rel" : icon , "href" : ""  }
        else:
            item["data"] = "%s <i>- (x %s)</i>" % (name, utils.print_integer(i.quantity))
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
            id = "_%d_%d_%d_%d" % (stationID, hangarID, container1, i.itemID)
            item["attr"] = { "id" : id , "rel" : icon , "href" : "", "class" : "%s-row" % icon  }
            item["state"] = "closed"
        elif i.singleton:
            item["data"] = name
            item["attr"] = { "rel" : icon , "href" : ""  }
        else:
            item["data"] = "%s <i>- (x %s)</i>" % (name, utils.print_integer(i.quantity))
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
        if i.singleton: 
            item["data"] = name
        else:
            item["data"] = "%s <i>- (x %s)</i>" % (name, utils.print_integer(i.quantity))
        item["attr"] = { "rel" : icon , "href" : ""  }
        json_data.append(item)
        
    return json_data

#------------------------------------------------------------------------------  
def search(search_string, divisions):
    matchingIDs = db.getMatchingIdsFromString(search_string)
    if divisions:
        matching_items = DbAsset.objects.filter(typeID__in=matchingIDs, hangarID__in=divisions)
    else:
        matching_items = DbAsset.objects.filter(typeID__in=matchingIDs)

    json_data = []

    for i in matching_items:
        nodeid = "#_%d" % i.locationID
        json_data.append(nodeid)
        nodeid = nodeid + "_%d" % i.hangarID
        json_data.append(nodeid)
        if i.container1:
            nodeid = nodeid + "_%d" % i.container1
            json_data.append(nodeid)
            if i.container2:
                nodeid = nodeid + "_%d" % i.container2
                json_data.append(nodeid)

    return json_data

