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

__date__ = '2011-05-21'
__author__ = 'diabeteman'


from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx
from django.template.defaultfilters import pluralize
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.db import connection
from django.db.models.query_utils import Q

from ecm.utils.format import round_quantity, print_float, print_integer
from ecm.utils import db
from ecm.utils import _json as json
from ecm.views.decorators import check_user_access
from ecm.apps.eve.models import CelestialObject, Type
from ecm.apps.eve import constants
from ecm.plugins.assets.models import Asset
from ecm.apps.corp.models import Corporation, Hangar, CorpHangar
from ecm.apps.common.models import Setting, UpdateDate
from ecm.plugins.assets.views import extract_divisions, HTML_ITEM_SPAN


CATEGORY_ICONS = { 2 : 'can' ,
                   4 : 'mineral' ,
                   6 : 'ship' ,
                   8 : 'ammo' ,
                   9 : 'blueprint',
                  16 : 'skill' }

#------------------------------------------------------------------------------
@check_user_access()
def root(request):
    scan_date = UpdateDate.get_latest(Asset)
    if scan_date == '<no data>':
        return render_to_response('ecm/assets/assets_no_data.html', Ctx(request))

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

    data = { 'show_in_space' : show_in_space,
          'show_in_stations' : show_in_stations,
             'divisions_str' : divisions_str,
                   'hangars' : all_hangars,
                 'scan_date' : scan_date }

    return render_to_response('ecm/assets/assets.html', data, Ctx(request))




#------------------------------------------------------------------------------

@check_user_access()
def get_systems_data(request):

    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))

    where = []
    if not show_in_space:
        where.append('"stationID" < %d' % constants.MAX_STATION_ID)
    if not show_in_stations:
        where.append('"stationID" > %d' % constants.MAX_STATION_ID)
    if divisions is not None:
        where.append('"hangarID" IN (%s)' % ', '.join(['%s'] * len(divisions)))

    sql = 'SELECT "solarSystemID", COUNT(*) AS "items", SUM("volume") AS "volume" '\
          'FROM "assets_asset" '
    if where: sql += ' WHERE ' + ' AND '.join(where)
    sql += ' GROUP BY "solarSystemID";'
    sql = db.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, divisions)

    exact_volumes = Setting.get('assets_show_exact_volumes')

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

        if exact_volumes:
            volume = print_float(volume)
        else:
            volume = round_quantity(volume)

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
def get_celestial_objects_data(request, solarSystemID):
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
        where.append('"hangarID" IN (%s)' % ', '.join(['%s'] * len(divisions)))

    sql = 'SELECT "closest_object_id", COUNT(*), SUM("volume") '\
          'FROM "assets_asset" '\
          'WHERE "solarSystemID"=%s '
    if where:
        sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "closest_object_id";'
    sql = db.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID])
    else:
        cursor.execute(sql, [solarSystemID] + list(divisions))

    exact_volumes = Setting.get('assets_show_exact_volumes')

    jstree_data = []
    for closest_object_id, items, volume in cursor:

        if closest_object_id != 0:
            try:
                name = CelestialObject.objects.get(itemID=closest_object_id).itemName
            except CelestialObject.DoesNotExist:
                name = str(closest_object_id)
        else:
            name = 'Stations'

        if exact_volumes:
            volume = print_float(volume)
        else:
            volume = round_quantity(volume)

        jstree_data.append({
            'data' : HTML_ITEM_SPAN % (name, items, pluralize(items), volume),
            'attr' : {
                'id' : '%d_%d_' % (solarSystemID, closest_object_id),
                'sort_key' : closest_object_id,
                'rel' : 'celestial',
                'class' : 'celestial-row',
            },
            'state' : 'closed'
        })
    cursor.close()
    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
def get_stations_data(request, solarSystemID, closest_obj_id):
    solarSystemID = int(solarSystemID)
    closest_obj_id = int(closest_obj_id)
    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))

    where = []
    if not show_in_space:
        where.append('"stationID" < %d' % constants.MAX_STATION_ID)
    if not show_in_stations:
        where.append('"stationID" > %d' % constants.MAX_STATION_ID)
    if divisions is not None:
        where.append('"hangarID" IN (%s)' % ', '.join(['%s'] * len(divisions)))

    sql = 'SELECT "stationID", MAX("name"), MAX("flag"), COUNT(*), SUM("volume") '\
          'FROM "assets_asset" '\
          'WHERE "solarSystemID"=%s AND "closest_object_id"=%s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "stationID";'
    sql = db.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID, closest_obj_id])
    else:
        cursor.execute(sql, [solarSystemID, closest_obj_id] + list(divisions))

    exact_volumes = Setting.get('assets_show_exact_volumes')

    jstree_data = []
    for stationID, item_name, flag, items, volume in cursor:
        if stationID < constants.MAX_STATION_ID:
            # it's a real station
            try:
                name = CelestialObject.objects.get(itemID=stationID).itemName
            except CelestialObject.DoesNotExist:
                name = str(stationID)
            icon = 'station'
        else:
            # it is an inspace anchorable array
            type_name = Type.objects.get(typeID=flag).typeName

            name = type_name
            if item_name and type_name != item_name:
                name += ' "%s"' % item_name

            if constants.CONTROL_TOWERS.has_key(flag):
                icon = 'pos'
            else:
                icon = 'array'

        if exact_volumes:
            volume = print_float(volume)
        else:
            volume = round_quantity(volume)

        jstree_data.append({
            'data' : HTML_ITEM_SPAN % (name, items, pluralize(items), volume),
            'attr' : {
                'id' : '%d_%d_%d_' % (solarSystemID, closest_obj_id, stationID),
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
def get_hangars_data(request, solarSystemID, closest_obj_id, stationID):
    solarSystemID = int(solarSystemID)
    closest_obj_id = int(closest_obj_id)
    stationID = int(stationID)
    divisions = extract_divisions(request)

    where = []
    if divisions is not None:
        where.append('"hangarID" IN (%s)' % ', '.join(['%s'] * len(divisions)))

    sql = 'SELECT "hangarID", COUNT(*) AS "items", SUM("volume") AS "volume" '\
          'FROM "assets_asset" '\
          'WHERE "solarSystemID"=%s AND "closest_object_id"=%s AND "stationID"=%s '
    if where: sql += ' AND ' + ' AND '.join(where)
    sql += ' GROUP BY "hangarID";'
    sql = db.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    if divisions is None:
        cursor.execute(sql, [solarSystemID, closest_obj_id, stationID])
    else:
        cursor.execute(sql, [solarSystemID, closest_obj_id, stationID] + list(divisions))

    exact_volumes = Setting.get('assets_show_exact_volumes')

    HANGAR = Hangar.DEFAULT_NAMES.copy()
    for h in CorpHangar.objects.filter(corp=Corporation.objects.mine()):
        HANGAR[h.hangar_id] = h.name

    jstree_data = []
    for hangarID, items, volume in cursor:

        if exact_volumes:
            volume = print_float(volume)
        else:
            volume = round_quantity(volume)

        jstree_data.append({
            'data': HTML_ITEM_SPAN % (HANGAR[hangarID], items, pluralize(items), volume),
            'attr' : {
                'id' : '%d_%d_%d_%d_' % (solarSystemID, closest_obj_id, stationID, hangarID),
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
def get_hangar_content_data(request, solarSystemID, closest_obj_id, stationID, hangarID):
    solarSystemID = int(solarSystemID)
    closest_obj_id = int(closest_obj_id)
    stationID = int(stationID)
    hangarID = int(hangarID)

    assets_query = Asset.objects.filter(solarSystemID=solarSystemID,
                                        stationID=stationID, hangarID=hangarID,
                                        container1=None, container2=None)

    jstree_data = []
    for a in assets_query.select_related(depth=1):

        try:
            icon = CATEGORY_ICONS[a.eve_type.categoryID]
        except KeyError:
            icon = 'item'

        if a.hasContents:
            data = a.eve_type.typeName
            if a.name and a.name != a.eve_type.typeName:
                data += ' "%s"' % a.name
            ID = '%d_%d_%d_%d_%d_' % (solarSystemID, closest_obj_id, stationID, hangarID, a.itemID)
            state = 'closed'
        elif a.singleton:
            data = a.eve_type.typeName
            ID = ''
            state = ''
        else:
            data = '%s <i>- (x %s)</i>' % (a.eve_type.typeName, print_integer(a.quantity))
            ID = ''
            state = ''

        jstree_data.append({
            'data': data,
            'attr' : {
                'id' : ID,
                'sort_key' : a.eve_type.typeName.lower(),
                'rel' : icon
            },
            'state' : state
        })

    return HttpResponse(json.dumps(jstree_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def get_can1_content_data(request, solarSystemID, closest_obj_id, stationID, hangarID, container1):
    solarSystemID = int(solarSystemID)
    closest_obj_id = int(closest_obj_id)
    stationID = int(stationID)
    hangarID = int(hangarID)
    container1 = int(container1)

    assets_query = Asset.objects.filter(solarSystemID=solarSystemID,
                                        stationID=stationID, hangarID=hangarID,
                                        container1=container1, container2=None)
    json_data = []
    for a in assets_query.select_related(depth=1):
        item = {}
        try:    icon = CATEGORY_ICONS[a.eve_type.categoryID]
        except: icon = 'item'

        if a.hasContents:
            item['data'] = a.eve_type.typeName
            ID = '%d_%d_%d_%d_%d_%d_' % (solarSystemID, closest_obj_id, stationID, hangarID, container1, a.itemID)
            item['attr'] = { 'id' : ID , 'rel' : icon , 'href' : '', 'class' : '%s-row' % icon  }
            item['state'] = 'closed'
        elif a.singleton:
            item['data'] = a.eve_type.typeName
            item['attr'] = { 'rel' : icon , 'href' : ''  }
        else:
            item['data'] = '%s <i>- (x %s)</i>' % (a.eve_type.typeName, print_integer(a.quantity))
            item['attr'] = { 'rel' : icon , 'href' : ''  }

        json_data.append(item)

    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def get_can2_content_data(request, solarSystemID, closest_obj_id, stationID, hangarID, container1, container2):
    assets_query = Asset.objects.filter(solarSystemID=int(solarSystemID),
                                        stationID=int(stationID),
                                        hangarID=int(hangarID),
                                        container1=int(container1),
                                        container2=int(container2))
    json_data = []
    for a in assets_query.select_related(depth=1):
        item = {}
        try:    icon = CATEGORY_ICONS[a.eve_type.category]
        except: icon = 'item'
        if a.singleton:
            item['data'] = a.eve_type.typeName
        else:
            item['data'] = '%s <i>- (x %s)</i>' % (a.eve_type.typeName, print_integer(a.quantity))
        item['attr'] = { 'rel' : icon , 'href' : ''  }
        json_data.append(item)

    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def search_items(request):

    divisions = extract_divisions(request)
    show_in_space = json.loads(request.GET.get('space', 'true'))
    show_in_stations = json.loads(request.GET.get('stations', 'true'))
    search_string = request.GET.get('search_string', None)

    filter_args = Q(name__icontains=search_string)
    if search_string:
        filter_args |= Q(eve_type__typeName__icontains=search_string)

    query = Asset.objects.filter(filter_args)

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
        nodeid = nodeid + '%d_' % item.closest_object_id
        json_data.append(nodeid)
        nodeid = nodeid + '%d_' % item.stationID
        json_data.append(nodeid)
        nodeid = nodeid + '%d_' % item.hangarID
        json_data.append(nodeid)
        if item.container1:
            nodeid = nodeid + '%d_' % item.container1
            json_data.append(nodeid)
            if item.container2:
                nodeid = nodeid + '%d_' % item.container2
                json_data.append(nodeid)

    return HttpResponse(json.dumps(json_data))
