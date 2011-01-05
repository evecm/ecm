'''
This file is part of ICE Security Management

Created on 25 dev 2010
@author: diabeteman
'''

import json
from datetime import datetime

from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import user_passes_test
from django.template.context import RequestContext
from django.template.defaultfilters import pluralize
from django.views.decorators.cache import cache_page
from django.http import HttpResponse

from ism.core import db, utils
from ism.data.common.models import UpdateDate
from ism.data.assets.models import DbAsset, DbAssetDiff
from ism.data.corp.models import Hangar
from ism import settings
from django.views.decorators.csrf import csrf_protect

DATE_PATTERN = "%Y-%m-%d_%H-%M-%S"

HANGAR = {}
for h in Hangar.objects.all():
    HANGAR[h.hangarID] = h.name

#------------------------------------------------------------------------------
def last_stations(request):
    # if called without date, redirect to the last date.

    datesDb = DbAssetDiff.objects.values("date").distinct().order_by("-date")
    date_str = datetime.strftime(datesDb[0]["date"], DATE_PATTERN)

    return redirect("/assets/changes/%s" % date_str)

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def stations(request, date_str):
    
    date = datetime.strptime(date_str, DATE_PATTERN)
    
    all_hangars = Hangar.objects.all()
    try: 
        divisions_str = request.GET["divisions"]
        divisions = tuple([ int(div) for div in divisions_str.split(",") ])
        for h in all_hangars: h.checked = (h.hangarID in divisions)
    except: 
        divisions, divisions_str = None, None
        for h in all_hangars: h.checked = False
    
    datesDb = DbAssetDiff.objects.values("date").distinct().order_by("-date")
    dates = []
    for d in datesDb:
        dates.append({ 
            "value" : datetime.strftime(d["date"], DATE_PATTERN),
            "show" : utils.print_time_min(d["date"])
        })

    data = {  'station_list' : getStations(date, divisions),
                 'divisions' : divisions, # divisions to show
             'divisions_str' : divisions_str,
                   'hangars' : all_hangars,
                     'dates' : dates,
                      'date' : utils.print_time_min(date),
                  'date_str' : date_str,
                 'scan_date' : getScanDate() }

    return render_to_response("assets_diff.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def hangars(request, date_str, stationID):
    
    date = datetime.strptime(date_str, DATE_PATTERN)

    try: divisions = tuple([ int(div) for div in request.GET["divisions"].split(",") ])
    except: divisions = None
    
    json_data = json.dumps(getStationHangars(date, int(stationID), divisions))
    
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def hangar_contents(request, date_str, stationID, hangarID):
    date = datetime.strptime(date_str, DATE_PATTERN)
    json_data = json.dumps(getHangarContents(date, int(stationID), int(hangarID)))
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def search_items(request, date_str):
    
    date = datetime.strptime(date_str, DATE_PATTERN)

    try: divisions = tuple([ int(div) for div in request.GET["divisions"].split(",") ])
    except: divisions = None
    
    search_string = request.GET.get("search_string", "no-item")
    
    json_data = json.dumps(doSearch(date, search_string, divisions))
    
    return HttpResponse(json_data)

#------------------------------------------------------------------------------

SQL_STATIONS_DIFF = "SELECT id, locationID, count(*) AS items, date FROM assets_dbassetdiff WHERE date='%s' GROUP BY locationID;"
SQL_STATIONS_DIFF_FILTERED = "SELECT id, locationID, count(*) AS items, date FROM assets_dbassetdiff WHERE date='%s' AND hangarID in %s GROUP BY locationID;"

def getStations(date, divisions):

    if divisions:
        raw_list = DbAssetDiff.objects.raw(SQL_STATIONS_DIFF_FILTERED % (utils.print_time(date), str(divisions)))
    else:
        raw_list = DbAssetDiff.objects.raw(SQL_STATIONS_DIFF % utils.print_time(date))
        
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

SQL_HANGARS = "SELECT id, hangarID, count(*) AS items FROM assets_dbassetdiff WHERE date='%s' AND locationID=%d GROUP BY hangarID ORDER BY hangarID;"
SQL_HANGARS_FILTERED = "SELECT id, hangarID, count(*) AS items FROM assets_dbassetdiff WHERE date='%s' AND locationID=%d AND hangarID in %s GROUP BY hangarID ORDER BY hangarID;"

def getStationHangars(date, stationID, divisions):
    if divisions:
        sql = SQL_HANGARS_FILTERED % (utils.print_time(date), stationID, str(divisions))
        raw_list = DbAssetDiff.objects.raw(sql)
    else:
        raw_list = DbAssetDiff.objects.raw(SQL_HANGARS % (utils.print_time(date), stationID))
        
    hangar_list = []
    for h in raw_list:
        hangar = {}
        hangar["data"] = '<b>%s</b><i> - (%d item%s changed)</i>' % (HANGAR[h.hangarID], h.items, pluralize(h.items))
        id = "_%d_%d" % (stationID, h.hangarID) 
        hangar["attr"] = { "id" : id , "rel" : "hangar" , "href" : "" }
        hangar["state"] = "closed"
        hangar_list.append(hangar)
    
    return hangar_list
#------------------------------------------------------------------------------
def getHangarContents(date, stationID, hangarID):
    item_list = DbAssetDiff.objects.filter(date=date, locationID=stationID, hangarID=hangarID)
    json_data = []
    for i in item_list:
        item = {}
        name, category = db.resolveTypeName(i.typeID)
        if i.quantity < 0:
            icon = "removed"
        else:
            icon = "added"

        item["data"] = "%s <i>(%s)</i>" % (name, utils.print_quantity(i.quantity))
        item["attr"] = { "rel" : icon , "href" : "" , "class" : "%s-row" % icon }
        json_data.append(item)
        
    return json_data

#------------------------------------------------------------------------------  
def doSearch(date, search_string, divisions):
    matchingIDs = db.getMatchingIdsFromString(search_string)
    if divisions:
        matching_items = DbAssetDiff.objects.filter(date=date, typeID__in=matchingIDs, hangarID__in=divisions)
    else:
        matching_items = DbAssetDiff.objects.filter(date=date, typeID__in=matchingIDs)

    json_data = []

    for i in matching_items:
        nodeid = "#_%d" % i.locationID
        json_data.append(nodeid)
        nodeid = nodeid + "_%d" % i.hangarID
        json_data.append(nodeid)

    return json_data



#------------------------------------------------------------------------------
def getScanDate():
    date = UpdateDate.objects.get(model_name=DbAsset.__name__) 
    return utils.print_time_min(date.update_date)
#------------------------------------------------------------------------------





