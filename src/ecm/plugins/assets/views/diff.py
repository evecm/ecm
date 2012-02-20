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

__date__ = '2010-12-25'

__author__ = 'diabeteman'

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json
from datetime import datetime, timedelta

from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext as Ctx
from django.template.defaultfilters import pluralize
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.db import connection

from ecm.views.decorators import check_user_access
from ecm.plugins.assets.views import extract_divisions, HTML_ITEM_SPAN
from ecm.core.eve import constants, db
from ecm.core import utils, JSON
from ecm.plugins.assets.models import Asset, AssetDiff
from ecm.apps.corp.models import Hangar
from ecm.views import getScanDate, DATE_PATTERN




#------------------------------------------------------------------------------
def last_date(request):
    # if called without date, redirect to the last date.
    since_weeks = int(request.GET.get('since_weeks', '8'))
    to_weeks = int(request.GET.get('to_weeks', '0'))
    oldest_date = datetime.now() - timedelta(weeks=since_weeks)
    newest_date = datetime.now() - timedelta(weeks=to_weeks)

    query = AssetDiff.objects.values_list('date', flat=True).distinct().order_by('-date')
    query = query.filter(date__gte=oldest_date)
    query = query.filter(date__lte=newest_date)

    try:
        last_date = query[0]
        date_str = datetime.strftime(last_date, DATE_PATTERN)
        return redirect('/assets/changes/%s/?since_weeks=%d&to_weeks=%d' % (date_str, since_weeks, to_weeks))
    except IndexError:
        return render_to_response('assets_no_data.html', context_instance=Ctx(request))


def get_dates(request):
    
    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))
    divisions = extract_divisions(request)

    since_weeks = int(request.GET.get('since_weeks', '8'))
    to_weeks = int(request.GET.get('to_weeks', '0'))

    oldest_date = datetime.now() - timedelta(weeks=since_weeks)
    newest_date = datetime.now() - timedelta(weeks=to_weeks)
    
    query = AssetDiff.objects.all()
    query = query.filter(date__gte=oldest_date)
    query = query.filter(date__lte=newest_date)
    if not show_in_space:
        query = query.filter(stationID__lt=constants.MAX_STATION_ID)
    if not show_in_stations:
        query = query.filter(stationID__gt=constants.MAX_STATION_ID)
    if divisions is not None:
        query = query.filter(hangarID__in=divisions)
        
    dates = []
    for date in query.values_list('date', flat=True).distinct().order_by('-date'):
        dates.append({
            'value' : datetime.strftime(date, DATE_PATTERN),
            'show' : utils.print_time_min(date),
        })
    
    return HttpResponse(json.dumps(dates))
    
    
    
    
    
    
    
    
#------------------------------------------------------------------------------
@check_user_access()
def root(request, date_str):

    all_hangars = Hangar.objects.all().order_by('hangarID')
    try:
        divisions_str = request.GET['divisions']
        divisions = [ int(div) for div in divisions_str.split(',') ]
        for h in all_hangars:
            h.checked = h.hangarID in divisions
    except:
        divisions, divisions_str = None, None
        for h in all_hangars:
            h.checked = True

    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))

    since_weeks = int(request.GET.get('since_weeks', '8'))
    to_weeks = int(request.GET.get('to_weeks', '0'))

    oldest_date = datetime.now() - timedelta(weeks=since_weeks)
    newest_date = datetime.now() - timedelta(weeks=to_weeks)

    query = AssetDiff.objects.values_list('date', flat=True).distinct().order_by('-date')
    query = query.filter(date__gte=oldest_date)
    query = query.filter(date__lte=newest_date)

    dates = []
    for date in query:
        dates.append({
            'value' : datetime.strftime(date, DATE_PATTERN),
            'show' : date
        })

    data = { 'show_in_space' : show_in_space,
          'show_in_stations' : show_in_stations,
             'divisions_str' : divisions_str,
                   'hangars' : all_hangars,
                 'scan_date' : getScanDate(Asset),
               'since_weeks' : since_weeks,
                  'to_weeks' : to_weeks,
                  'date_str' : date_str,
                     'dates' : dates }

    try:
        date_asked = datetime.strptime(date_str, DATE_PATTERN)
        if AssetDiff.objects.filter(date=date_asked).exists():
            data['date'] = date_asked
            return render_to_response('assets_diff.html', data, Ctx(request))
        else:
            return render_to_response('assets_no_data.html', Ctx(request))
    except:
        return redirect('/assets/changes/')


#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def systems_data(request, date_str):
    date = datetime.strptime(date_str, DATE_PATTERN)
    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))

    where = []
    if not show_in_space:
        where.append('"stationID" < %d' % constants.MAX_STATION_ID)
    if not show_in_stations:
        where.append('"stationID" > %d' % constants.MAX_STATION_ID)
    if divisions is not None:
        s = ('%s,' * len(divisions))[:-1]
        where.append('"hangarID" IN (%s)' % s)

    sql = 'SELECT "solarSystemID", COUNT(*) AS "items", SUM("volume") AS "volume" '
    sql += 'FROM "assets_assetdiff" '
    sql += 'WHERE date=%s'
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "solarSystemID";'
    sql = utils.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [date])
    else:
        cursor.execute(sql, [date] + list(divisions))

    jstree_data = []
    for solarSystemID, items, volume in cursor:
        name, security = db.resolveLocationName(solarSystemID)
        if security > 0.5:
            color = 'hisec'
        elif security > 0:
            color = 'lowsec'
        else:
            color = 'nullsec'
        jstree_data.append({
            'data' : HTML_ITEM_SPAN % (name, items, pluralize(items), volume),
            'attr' : {
                'id' : '%d_' % solarSystemID,
                'rel' : 'system',
                'sort_key' : name.lower(),
                'class' : 'system-%s-row' % color
            },
            'state' : 'closed'
        })
    cursor.close()
    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def stations_data(request, date_str, solarSystemID):
    date = datetime.strptime(date_str, DATE_PATTERN)
    solarSystemID = int(solarSystemID)
    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))

    where = []
    if not show_in_space:
        where.append('"stationID" < %d' % constants.MAX_STATION_ID)
    if not show_in_stations:
        where.append('"stationID" > %d' % constants.MAX_STATION_ID)
    if divisions is not None:
        s = ('%s,' * len(divisions))[:-1]
        where.append('"hangarID" IN (%s)' % s)

    sql = 'SELECT "stationID", MAX("flag") as "flag", COUNT(*) AS "items", SUM("volume") AS "volume" '
    sql += 'FROM "assets_assetdiff" '
    sql += 'WHERE "solarSystemID"=%s AND "date"=%s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "stationID";'
    sql = utils.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID, date])
    else:
        cursor.execute(sql, [solarSystemID, date] + list(divisions))

    jstree_data = []
    for stationID, flag, items, volume in cursor:
        if stationID < constants.MAX_STATION_ID:
            # it's a real station
            name = db.resolveLocationName(stationID)[0]
            icon = 'station'
        else:
            # it is an inspace anchorable array
            name = db.get_type_name(flag)[0]
            icon = 'array'

        jstree_data.append({
            'data' : HTML_ITEM_SPAN % (name, items, pluralize(items), volume),
            'attr' : {
                'id' : '%d_%d_' % (solarSystemID, stationID),
                'sort_key' : stationID,
                'rel' : icon,
                'class' : '%s-row' % icon
            },
            'state' : 'closed'
        })
    cursor.close()
    return HttpResponse(json.dumps(jstree_data))


#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def hangars_data(request, date_str, solarSystemID, stationID):

    date = datetime.strptime(date_str, DATE_PATTERN)
    solarSystemID = int(solarSystemID)
    stationID = int(stationID)
    divisions = extract_divisions(request)

    where = []
    if divisions is not None:
        s = ('%s,' * len(divisions))[:-1]
        where.append('"hangarID" IN (%s)' % s)

    sql = 'SELECT "hangarID", COUNT(*) AS "items", SUM("volume") AS "volume" '
    sql += 'FROM "assets_assetdiff" '
    sql += 'WHERE "solarSystemID"=%s AND "stationID"=%s AND "date"=%s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "hangarID";'
    sql = utils.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID, stationID, date])
    else:
        cursor.execute(sql, [solarSystemID, stationID, date] + list(divisions))

    HANGAR = {}
    for h in Hangar.objects.all():
        HANGAR[h.hangarID] = h.name

    jstree_data = []
    for hangarID, items, volume in cursor.fetchall():
        jstree_data.append({
            'data': HTML_ITEM_SPAN % (HANGAR[hangarID], items, pluralize(items), volume),
            'attr' : {
                'id' : '%d_%d_%d_' % (solarSystemID, stationID, hangarID),
                'sort_key' : hangarID,
                'rel' : 'hangar',
                'class' : 'hangar-row'
            },
            'state' : 'closed'
        })

    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def hangar_contents_data(request, date_str, solarSystemID, stationID, hangarID):
    date = datetime.strptime(date_str, DATE_PATTERN)
    solarSystemID = int(solarSystemID)
    stationID = int(stationID)
    hangarID = int(hangarID)

    query = AssetDiff.objects.filter(solarSystemID=solarSystemID,
                                     stationID=stationID, hangarID=hangarID,
                                     date=date)
    jstree_data = []
    for item in query:
        name = db.get_type_name(item.typeID)[0]

        if item.quantity < 0:
            icon = 'removed'
        else:
            icon = 'added'

        jstree_data.append({
            'data': '%s <i>(%s)</i>' % (name, utils.print_integer(item.quantity)),
            'attr' : {
                'sort_key' : name.lower(),
                'rel' : icon,
                'class' : '%s-row' % icon
            }
        })

    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def search_items(request, date_str):
    date = datetime.strptime(date_str, DATE_PATTERN)
    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))
    search_string = request.GET.get('search_string', 'no-item')

    matchingIDs = db.getMatchingIdsFromString(search_string)

    query = AssetDiff.objects.filter(typeID__in=matchingIDs, date=date)

    if divisions is not None:
        query = query.filter(hangarID__in=divisions)
    if not show_in_space:
        query = query.filter(stationID__lt=constants.MAX_STATION_ID)
    if not show_in_stations:
        query = query.filter(stationID__gt=constants.MAX_STATION_ID)


    json_data = []

    for item in query:
        nodeid = '#%d_' % item.solarSystemID
        json_data.append(nodeid)
        nodeid = nodeid + '%d_' % item.stationID
        json_data.append(nodeid)
        nodeid = nodeid + '%d_' % item.hangarID
        json_data.append(nodeid)

    return HttpResponse(json.dumps(json_data))
