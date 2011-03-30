"""
The MIT License - EVE Corporation Management

Copyright (c) 2010 Robin Jarry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__date__ = "2010-12-25"
__author__ = "diabeteman"

import json
from datetime import datetime, timedelta

from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import user_passes_test
from django.template.context import RequestContext
from django.template.defaultfilters import pluralize
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from ecm.core import db, utils
from ecm.data.assets.models import DbAsset, DbAssetDiff
from ecm.data.corp.models import Hangar
from ecm import settings
from django.views.decorators.csrf import csrf_protect
from ecm.view import getScanDate

DATE_PATTERN = "%Y-%m-%d_%H-%M-%S"



#------------------------------------------------------------------------------
def last_stations(request):
    # if called without date, redirect to the last date.

    since_weeks = int(request.GET.get("since_weeks", "8"))
    to_weeks = int(request.GET.get("to_weeks", "0"))
    oldest_date = datetime.now() - timedelta(weeks=since_weeks)
    newest_date = datetime.now() - timedelta(weeks=to_weeks)

    datesDb = DbAssetDiff.objects.values("date").distinct().order_by("-date")
    datesDb = datesDb.filter(date__gte=oldest_date)
    datesDb = datesDb.filter(date__lte=newest_date)
    
    try:
        date_str = datetime.strftime(datesDb[0]["date"], DATE_PATTERN)
        return redirect("/assets/changes/%s?since_weeks=%d&to_weeks=%d" % (date_str, since_weeks, to_weeks))
    except:
        return render_to_response("assets/assets_no_data.html", context_instance=RequestContext(request))



#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def stations(request, date_str):
    
    all_hangars = Hangar.objects.all()
    try: 
        divisions_str = request.GET["divisions"]
        divisions = [ int(div) for div in divisions_str.split(",") ]
        for h in all_hangars: h.checked = (h.hangarID in divisions)
    except: 
        divisions, divisions_str = None, None
        for h in all_hangars: h.checked = False
    
    since_weeks = int(request.GET.get("since_weeks", "8"))
    to_weeks = int(request.GET.get("to_weeks", "0"))
    
    oldest_date = datetime.now() - timedelta(weeks=since_weeks)
    newest_date = datetime.now() - timedelta(weeks=to_weeks)
    
    datesDb = DbAssetDiff.objects.values_list("date", flat=True).distinct().order_by("-date")
    datesDb = datesDb.filter(date__gte=oldest_date)
    datesDb = datesDb.filter(date__lte=newest_date)
    
    dates = []
    for date in datesDb:
        dates.append({ 
            "value" : datetime.strftime(date, DATE_PATTERN),
            "show" : utils.print_time_min(date)
        })

    date = datetime.strptime(date_str, DATE_PATTERN)
    stations = getStations(date, divisions)

    data = {  'station_list' : stations,
                 'divisions' : divisions, # divisions to show
             'divisions_str' : divisions_str,
                   'hangars' : all_hangars,
                     'dates' : dates,
                      'date' : utils.print_time_min(date),
                  'date_str' : date_str,
                 'scan_date' : getScanDate(DbAsset.__name__),
               'since_weeks' : since_weeks,
                  'to_weeks' : to_weeks }

    if stations:
        return render_to_response("assets/assets_diff.html", data, context_instance=RequestContext(request))
    else:
        return HttpResponseNotFound()

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def hangars(request, date_str, stationID):
    
    date = datetime.strptime(date_str, DATE_PATTERN)

    try: divisions = [ int(div) for div in request.GET["divisions"].split(",") ]
    except: divisions = None
    
    json_data = json.dumps(getStationHangars(date, int(stationID), divisions))
    
    return HttpResponse(json_data)

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def hangar_contents(request, date_str, stationID, hangarID):
    date = datetime.strptime(date_str, DATE_PATTERN)
    hangar_contents = getHangarContents(date, int(stationID), int(hangarID))
    if hangar_contents:
        return HttpResponse(json.dumps(hangar_contents))
    else:
        return HttpResponseNotFound()

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def search_items(request, date_str):
    
    date = datetime.strptime(date_str, DATE_PATTERN)

    try: divisions = [ int(div) for div in request.GET["divisions"].split(",") ]
    except: divisions = None
    
    search_string = request.GET.get("search_string", None)
    
    if not search_string:
        return HttpResponseBadRequest()
    
    search_result = doSearch(date, search_string, divisions)
    
    return HttpResponse(json.dumps(search_result))

#------------------------------------------------------------------------------

SQL_STATIONS_DIFF = "SELECT id, locationID, count(*) AS items, date FROM assets_dbassetdiff WHERE date='%s' GROUP BY locationID;"
SQL_STATIONS_DIFF_FILTERED = "SELECT id, locationID, count(*) AS items, date FROM assets_dbassetdiff WHERE date='%s' AND hangarID in %s GROUP BY locationID;"

def getStations(date, divisions):

    if divisions:
        str_divisions = str(divisions).replace("[", "(").replace("]", ")")
        raw_list = DbAssetDiff.objects.raw(SQL_STATIONS_DIFF_FILTERED % (utils.print_time(date), str_divisions))
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
        str_divisions = str(divisions).replace("[", "(").replace("]", ")")
        sql = SQL_HANGARS_FILTERED % (utils.print_time(date), stationID, str_divisions)
        raw_list = DbAssetDiff.objects.raw(sql)
    else:
        raw_list = DbAssetDiff.objects.raw(SQL_HANGARS % (utils.print_time(date), stationID))
    
    HANGAR = {}
    for h in Hangar.objects.all():
        HANGAR[h.hangarID] = h.name
    
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
        name = db.resolveTypeName(i.typeID)[0]
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


