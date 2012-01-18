# Copyright (c) 2010-2012 Robin Jarry
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

__date__ = "2011-05-21"
__author__ = "diabeteman"



try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.defaultfilters import pluralize
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.db import connection

from ecm.views.decorators import check_user_access
from ecm.core.eve import constants, db
from ecm.core import utils
from ecm.plugins.assets.models import Asset
from ecm.apps.corp.models import Hangar
from ecm.views import getScanDate
from ecm.plugins.assets.views import extract_divisions, HTML_ITEM_SPAN


CATEGORY_ICONS = { 2 : "can" ,
                   4 : "mineral" ,
                   6 : "ship" ,
                   8 : "ammo" ,
                   9 : "blueprint",
                  16 : "skill" }

#------------------------------------------------------------------------------
@check_user_access()
def root(request):
    scan_date = getScanDate(Asset)
    if scan_date == "<no data>":
        return render_to_response("assets_no_data.html", RequestContext(request))

    all_hangars = Hangar.objects.all().order_by("hangarID")
    try:
        divisions_str = request.GET["divisions"]
        divisions = [ int(div) for div in divisions_str.split(",") ]
        for h in all_hangars:
            h.checked = h.hangarID in divisions
    except:
        divisions, divisions_str = None, None
        for h in all_hangars:
            h.checked = True

    show_in_space = json.loads(request.GET.get("space", "true"))
    show_in_stations = json.loads(request.GET.get("stations", "true"))

    data = { 'show_in_space' : show_in_space,
          'show_in_stations' : show_in_stations,
             'divisions_str' : divisions_str,
                   'hangars' : all_hangars,
                 'scan_date' : scan_date }

    return render_to_response("assets.html", data, RequestContext(request))




#------------------------------------------------------------------------------

@check_user_access()
def systems_data(request):

    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get("space", "true"))
    show_in_stations = json.loads(request.GET.get("stations", "true"))

    where = []
    if not show_in_space:
        where.append('"stationID" < %d' % constants.MAX_STATION_ID)
    if not show_in_stations:
        where.append('"stationID" > %d' % constants.MAX_STATION_ID)
    if divisions is not None:
        s = ('%s,' * len(divisions))[:-1]
        where.append('"hangarID" IN (%s)' % s)

    sql = 'SELECT "solarSystemID", COUNT(*) AS "items", SUM("volume") AS "volume" '\
          'FROM "assets_asset"'
    if where: sql += ' WHERE ' + ' AND '.join(where)
    sql += ' GROUP BY "solarSystemID";'
    sql = utils.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, divisions)

    jstree_data = []
    for solarSystemID, items, volume in cursor:
        name, security = db.resolveLocationName(solarSystemID)
        if security > 0.5:
            color = "hisec"
        elif security > 0:
            color = "lowsec"
        else:
            color = "nullsec"
        jstree_data.append({
            "data" : HTML_ITEM_SPAN % (name, items, pluralize(items)) + ' %s m3' % volume,
            "attr" : {
                "id" : "_%d" % solarSystemID,
                "rel" : "system",
                "sort_key" : name.lower(),
                "class" : "system-%s-row" % color
            },
            "state" : "closed"
        })
    cursor.close()
    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
def stations_data(request, solarSystemID):
    solarSystemID = int(solarSystemID)
    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get("space", "true"))
    show_in_stations = json.loads(request.GET.get("stations", "true"))

    where = []
    if not show_in_space:
        where.append('"stationID" < %d' % constants.MAX_STATION_ID)
    if not show_in_stations:
        where.append('"stationID" > %d' % constants.MAX_STATION_ID)
    if divisions is not None:
        s = ('%s,' * len(divisions))[:-1]
        where.append('"hangarID" IN (%s)' % s)

    sql = 'SELECT "stationID", MAX("flag") as "flag", COUNT(*) AS "items" FROM "assets_asset" '
    sql += 'WHERE "solarSystemID"=%s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "stationID";'
    sql = utils.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID])
    else:
        cursor.execute(sql, [solarSystemID] + list(divisions))

    jstree_data = []
    for stationID, flag, items in cursor:
        if stationID < constants.MAX_STATION_ID:
            # it's a real station
            name = db.resolveLocationName(stationID)[0]
            icon = "station"
        else:
            # it is an inspace anchorable array
            name = db.resolveTypeName(flag)[0]
            icon = "array"

        jstree_data.append({
            "data" : HTML_ITEM_SPAN % (name, items, pluralize(items)),
            "attr" : {
                "id" : "_%d_%d" % (solarSystemID, stationID),
                "sort_key" : stationID,
                "rel" : icon,
                "class" : "%s-row" % icon
            },
            "state" : "closed"
        })
    cursor.close()
    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def hangars_data(request, solarSystemID, stationID):
    solarSystemID = int(solarSystemID)
    stationID = int(stationID)
    divisions = extract_divisions(request)

    where = []
    if divisions is not None:
        s = ('%s,' * len(divisions))[:-1]
        where.append('"hangarID" IN (%s)' % s)

    sql = 'SELECT "hangarID", COUNT(*) AS "items" FROM "assets_asset" '
    sql += 'WHERE "solarSystemID"=%s AND "stationID"=%s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "hangarID";'
    sql = utils.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID, stationID])
    else:
        cursor.execute(sql, [solarSystemID, stationID] + list(divisions))

    HANGAR = {}
    for h in Hangar.objects.all():
        HANGAR[h.hangarID] = h.name

    jstree_data = []
    for hangarID, items in cursor:
        jstree_data.append({
            "data": HTML_ITEM_SPAN % (HANGAR[hangarID], items, pluralize(items)),
            "attr" : {
                "id" : "_%d_%d_%d" % (solarSystemID, stationID, hangarID),
                "sort_key" : hangarID,
                "rel" : "hangar",
                "class" : "hangar-row"
            },
            "state" : "closed"
        })

    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def hangar_content_data(request, solarSystemID, stationID, hangarID):
    solarSystemID = int(solarSystemID)
    stationID = int(stationID)
    hangarID = int(hangarID)

    query = Asset.objects.filter(solarSystemID=solarSystemID,
                                 stationID=stationID, hangarID=hangarID,
                                 container1=None, container2=None)
    jstree_data = []
    for item in query:
        name, category = db.resolveTypeName(item.typeID)

        try:
            icon = CATEGORY_ICONS[category]
        except KeyError:
            icon = "item"

        if item.hasContents:
            data = name
            ID = "_%d_%d_%d_%d" % (solarSystemID, stationID, hangarID, item.itemID)
            state = "closed"
        elif item.singleton:
            data = name
            ID = ""
            state = ""
        else:
            data = "%s <i>- (x %s)</i>" % (name, utils.print_integer(item.quantity))
            ID = ""
            state = ""

        jstree_data.append({
            "data": data,
            "attr" : {
                "id" : ID,
                "sort_key" : name.lower(),
                "rel" : icon
            },
            "state" : state
        })

    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def can1_content_data(request, solarSystemID, stationID, hangarID, container1):
    solarSystemID = int(solarSystemID)
    stationID = int(stationID)
    hangarID = int(hangarID)
    container1 = int(container1)

    item_list = Asset.objects.filter(solarSystemID=solarSystemID,
                                     stationID=stationID, hangarID=hangarID,
                                     container1=container1, container2=None)
    json_data = []
    for i in item_list:
        item = {}
        name, category = db.resolveTypeName(i.typeID)
        try:    icon = CATEGORY_ICONS[category]
        except: icon = "item"

        if i.hasContents:
            item["data"] = name
            ID = "_%d_%d_%d_%d_%d" % (solarSystemID, stationID, hangarID, container1, i.itemID)
            item["attr"] = { "id" : ID , "rel" : icon , "href" : "", "class" : "%s-row" % icon  }
            item["state"] = "closed"
        elif i.singleton:
            item["data"] = name
            item["attr"] = { "rel" : icon , "href" : ""  }
        else:
            item["data"] = "%s <i>- (x %s)</i>" % (name, utils.print_integer(i.quantity))
            item["attr"] = { "rel" : icon , "href" : ""  }

        json_data.append(item)

    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def can2_content_data(request, solarSystemID, stationID, hangarID, container1, container2):
    solarSystemID = int(solarSystemID)
    stationID = int(stationID)
    hangarID = int(hangarID)
    container1 = int(container1)
    container2 = int(container2)
    item_list = Asset.objects.filter(solarSystemID=solarSystemID,
                                     stationID=stationID, hangarID=hangarID,
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

    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def search_items(request):

    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get("space", "true"))
    show_in_stations = json.loads(request.GET.get("stations", "true"))
    search_string = request.GET.get("search_string", "no-item")

    matchingIDs = db.getMatchingIdsFromString(search_string)

    query = Asset.objects.filter(typeID__in=matchingIDs)

    if divisions is not None:
        query = query.filter(hangarID__in=divisions)
    if not show_in_space:
        query = query.filter(stationID__lt=constants.MAX_STATION_ID)
    if not show_in_stations:
        query = query.filter(stationID__gt=constants.MAX_STATION_ID)


    json_data = []

    for item in query:
        nodeid = "#_%d" % item.solarSystemID
        json_data.append(nodeid)
        nodeid = nodeid + "_%d" % item.stationID
        json_data.append(nodeid)
        nodeid = nodeid + "_%d" % item.hangarID
        json_data.append(nodeid)
        if item.container1:
            nodeid = nodeid + "_%d" % item.container1
            json_data.append(nodeid)
            if item.container2:
                nodeid = nodeid + "_%d" % item.container2
                json_data.append(nodeid)

    return HttpResponse(json.dumps(json_data))
