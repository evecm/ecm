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

from datetime import datetime, timedelta

from django.utils import timezone
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext as Ctx
from django.template.defaultfilters import pluralize
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.db import connection

from ecm.utils import db
from ecm.utils import _json as json
from ecm.apps.common.models import UpdateDate
from ecm.utils.format import print_integer, print_time_min
from ecm.views.decorators import check_user_access
from ecm.plugins.assets.views import extract_divisions, HTML_ITEM_SPAN
from ecm.apps.eve.models import CelestialObject, Type
from ecm.apps.eve import constants
from ecm.plugins.assets.models import Asset, AssetDiff
from ecm.apps.corp.models import CorpHangar, Corporation, Hangar
from ecm.views import DATE_PATTERN


#------------------------------------------------------------------------------
def last_date(request):
    # if called without date, redirect to the last date.
    since_weeks = int(request.GET.get('since_weeks', '8'))
    to_weeks = int(request.GET.get('to_weeks', '0'))
    oldest_date = timezone.now() - timedelta(weeks=since_weeks)
    newest_date = timezone.now() - timedelta(weeks=to_weeks)

    query = AssetDiff.objects.values_list('date', flat=True).distinct().order_by('-date')
    query = query.filter(date__gte=oldest_date)
    query = query.filter(date__lte=newest_date)

    try:
        last_date = query[0]
        date_str = datetime.strftime(last_date, DATE_PATTERN)
        return redirect('/assets/changes/%s/?since_weeks=%d&to_weeks=%d' % (date_str, since_weeks, to_weeks))
    except IndexError:
        return render_to_response('ecm/assets/assets_no_data.html', context_instance=Ctx(request))

#------------------------------------------------------------------------------
def get_dates(request):

    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))
    divisions = extract_divisions(request)

    since_weeks = int(request.GET.get('since_weeks', '8'))
    to_weeks = int(request.GET.get('to_weeks', '0'))

    oldest_date = timezone.now() - timedelta(weeks=since_weeks)
    newest_date = timezone.now() - timedelta(weeks=to_weeks)

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
            'show' : print_time_min(date),
        })

    return HttpResponse(json.dumps(dates))

#------------------------------------------------------------------------------
@check_user_access()
def root(request, date_str):

    my_corp = Corporation.objects.mine()
    all_hangars = Hangar.objects.all().order_by('hangarID')
    for hangar in all_hangars:
        hangar.name = hangar.get_name(my_corp)

    try:
        divisions_str = request.GET['divisions']
        divisions = [ int(div) for div in divisions_str.split(',') ]
        for h in all_hangars:
            h.checked = h.hangar_id in divisions
    except:
        divisions, divisions_str = None, None
        for h in all_hangars:
            h.checked = True

    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))

    since_weeks = int(request.GET.get('since_weeks', '8'))
    to_weeks = int(request.GET.get('to_weeks', '0'))

    oldest_date = timezone.now() - timedelta(weeks=since_weeks)
    newest_date = timezone.now() - timedelta(weeks=to_weeks)

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
                 'scan_date' : UpdateDate.get_latest(Asset),
               'since_weeks' : since_weeks,
                  'to_weeks' : to_weeks,
                  'date_str' : date_str,
                     'dates' : dates }

    try:
        date_asked = datetime.strptime(date_str, DATE_PATTERN)
        date_asked = timezone.make_aware(date_asked, timezone.utc)
        next_date = date_asked + timedelta(seconds=1)
    except ValueError:
        return redirect('/assets/changes/')

    if AssetDiff.objects.filter(date__range=(date_asked, next_date)).exists():
        data['date'] = date_asked
        return render_to_response('ecm/assets/assets_diff.html', data, Ctx(request))
    else:
        return render_to_response('ecm/assets/assets_no_data.html', {}, Ctx(request))


#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def get_systems_data(request, date_str):
    date = datetime.strptime(date_str, DATE_PATTERN)
    date = timezone.make_aware(date, timezone.utc)
    next_date = date + timedelta(seconds=1)

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
    # TODO: fix this sql into an object
    sql = 'SELECT "solarSystemID", COUNT(*) AS "items", SUM("volume") AS "volume" '
    sql += 'FROM "assets_assetdiff" '
    sql += 'WHERE date >= %s AND date < %s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "solarSystemID";'
    sql = db.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [date, next_date])
    else:
        cursor.execute(sql, [date, next_date] + list(divisions))

    jstree_data = []
    for solarSystemID, items, volume in cursor:
        try:
            system = CelestialObject.objects.get(itemID=solarSystemID)
        except CelestialObject.DoesNotExist:
            system = CelestialObject(itemID=solarSystemID, itemName=str(solarSystemID), security=0)
        if system.security > 0.5:
            color = 'hisec'
        elif system.security > 0:
            color = 'lowsec'
        else:
            color = 'nullsec'
        jstree_data.append({
            'data' : HTML_ITEM_SPAN % (system.itemName, items, pluralize(items), volume),
            'attr' : {
                'id' : '%d_' % solarSystemID,
                'rel' : 'system',
                'sort_key' : system.itemName.lower(),
                'class' : 'system-%s-row' % color
            },
            'state' : 'closed'
        })
    cursor.close()
    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def get_stations_data(request, date_str, solarSystemID):
    date = datetime.strptime(date_str, DATE_PATTERN)
    date = timezone.make_aware(date, timezone.utc)
    next_date = date + timedelta(seconds=1)
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
    sql += 'WHERE "solarSystemID"=%s AND "date" >= %s AND "date" < %s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "stationID";'
    sql = db.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID, date, next_date])
    else:
        cursor.execute(sql, [solarSystemID, date, next_date] + list(divisions))

    jstree_data = []
    for stationID, flag, items, volume in cursor:
        if stationID < constants.MAX_STATION_ID:
            # it's a real station
            try:
                name = CelestialObject.objects.get(itemID=stationID).itemName
            except CelestialObject.DoesNotExist:
                name = str(stationID)
            icon = 'station'
        else:
            # it is an inspace anchorable array
            name = Type.objects.get(typeID=flag).typeName
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
def get_hangars_data(request, date_str, solarSystemID, stationID):

    date = datetime.strptime(date_str, DATE_PATTERN)
    date = timezone.make_aware(date, timezone.utc)
    next_date = date + timedelta(seconds=1)
    solarSystemID = int(solarSystemID)
    stationID = int(stationID)
    divisions = extract_divisions(request)

    where = []
    if divisions is not None:
        s = ('%s,' * len(divisions))[:-1]
        where.append('"hangarID" IN (%s)' % s)

    sql = 'SELECT "hangarID", COUNT(*) AS "items", SUM("volume") AS "volume" '
    sql += 'FROM "assets_assetdiff" '
    sql += 'WHERE "solarSystemID"=%s AND "stationID"=%s AND "date" >= %s AND "date" < %s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "hangarID";'
    sql = db.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID, stationID, date, next_date])
    else:
        cursor.execute(sql, [solarSystemID, stationID, date, next_date] + list(divisions))

    HANGAR = Hangar.DEFAULT_NAMES.copy()
    for h in CorpHangar.objects.filter(corp=Corporation.objects.mine()):
        HANGAR[h.hangar_id] = h.name

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
def get_hangar_content_data(request, date_str, solarSystemID, stationID, hangarID):

    date = datetime.strptime(date_str, DATE_PATTERN)
    date = timezone.make_aware(date, timezone.utc)
    next_date = date + timedelta(seconds=1)

    assets_query = AssetDiff.objects.filter(solarSystemID=int(solarSystemID),
                                            stationID=int(stationID),
                                            hangarID=int(hangarID),
                                            date__range=(date, next_date))
    jstree_data = []
    for a in assets_query.select_related(depth=1):

        if a.quantity < 0:
            icon = 'removed'
        else:
            icon = 'added'

        jstree_data.append({
            'data': '%s <i>(%s)</i>' % (a.eve_type.typeName, print_integer(a.quantity)),
            'attr' : {
                'sort_key' : a.eve_type.typeName.lower(),
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
    date = timezone.make_aware(date, timezone.utc)
    next_date = date + timedelta(seconds=1)
    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))
    search_string = request.GET.get('search_string', None)

    query = AssetDiff.objects.filter(eve_type__typeName__icontains=search_string)
    query = query.filter(date__range=(date, next_date))

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
