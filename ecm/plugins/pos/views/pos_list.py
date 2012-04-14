# Copyright (c) 2011 jerome Vacher
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

__date__ = "2011-04-25"
__author__ = "JerryKhan"

try:
    import json
except ImportError:
    import django.utils.simplejson as json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.utils import db
from ecm.utils.format import print_duration
from ecm.plugins.pos.views import print_fuel_quantity
from ecm.plugins.pos.models import POS, FuelLevel
from ecm.views import extract_datatable_params
from ecm.views.decorators import check_user_access

from ecm.plugins.pos import constants as C

import logging
LOG = logging.getLogger(__name__)

# This table gives the association between the status of the POS
# and the related CSS class for display
POS_CSS_STATUS = {
    0: 'pos-unanchored',
    1: 'pos-offline',
    2: 'pos-onlining',
    3: 'pos-reinforced',
    4: 'pos-online',
}

#------------------------------------------------------------------------------
COLUMNS = [
    # Name              Tooltip                 db_field
    ['Location',        'Location',             'moon'],
    ['Name',            'Name',                 'custom_name'],
    ['Type',            'Type',                 'type_id'],
    ['Status',          'Status',               'state'],
    ['Time To Tick',    'Cycle Time',           'online_timestamp'],
    ['Fuel Blocks',     'Fuel Blocks',          None],
    ['Strontium',       'Strontium Clathrates', None],
    ['Name',            None,                   None],
    ['hours_int',       None,                   None],
]
@check_user_access()
def poses(request):
    data = {
        'posViewMode' : 'List',
        'columns' : [ (col, title) for col, title, _ in COLUMNS ],
        'posCSSStatus' : json.dumps(POS_CSS_STATUS),
        'posTextStatus' : json.dumps(POS.STATES),
    }
    return render_to_response("pos_list.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def poses_data(request):
    '''
    Read data when table request by Ajax.
    This method takes into account search filter and segmentation table
    Read the http request (GET method handling)
    '''
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.displayMode = REQ.get('displayMode', 'days')
    except:
        return HttpResponseBadRequest()
    print params.column
    
    
    # Query all by default.
    query = POS.objects.all().select_related(depth=1)
    
    # Only show POS for user group, where group filter applies
    query = query.filter(group_filter__group__in=request.user.groups.values('id'))
    # Then get the database content and translate to display table
    # manage the search filter
    if params.search:
        total_count = query.count()
        query = POS.objects.filter(moon__icontains=params.search)
        filtered_count = query.count()
    else:
        total_count = filtered_count = query.count()

    sort_col = COLUMNS[params.column][2]
    if params.column == 1:
        # SQL hack for making a case insensitive sort
        sort_col = sort_col + "_nocase"
        sort_val = db.fix_mysql_quotes('LOWER("%s")' % COLUMNS[params.column][2])
        query = query.extra(select={ sort_col : sort_val })
    elif params.column in (5, 6):
        # if sorting by fuel or stront. make a sorted list of (hoursleft|quantity,pos)
        # so that we can easily present and sort the data.
        pos_by_timeleft = []
        if params.displayMode == 'quantities':
            for pos in query:
                if params.column == 5:
                    quantity = pos.fuel_levels.filter(type_id=pos.fuel_type_id).latest().quantity
                else:
                    quantity = pos.fuel_levels.filter(type_id=C.STRONTIUM_CLATHRATES_TYPEID).latest().quantity
                pos_by_timeleft.append( (quantity, pos, pos.state) )
        else:
            for pos in query:
                if params.column == 5:
                    time_left = getFuelValue(pos, pos.fuel_type_id, 'hours_int')
                else:
                    time_left = getFuelValue(pos, C.STRONTIUM_CLATHRATES_TYPEID, 'hours_int')
                pos_by_timeleft.append( (time_left, pos, pos.state) )

        if not params.asc:
            pos_by_timeleft.sort(reverse=True)
        else:
            pos_by_timeleft.sort()
        for i, item in enumerate(pos_by_timeleft):
            if item[2] == 3:
                pos_by_timeleft.insert(0, pos_by_timeleft.pop(i))
    try:
        # This will fail if sorting by fuel.
        if not params.asc:
            sort_col = "-" + sort_col
    except TypeError:
        pass
    query = query.extra(order_by=('state', sort_col))

    pos_table = []
    if params.column < 5:
        for pos in query[params.first_id:params.last_id]:
            # Query into Fuel table to get last values. for the current POS
            if pos.state == 3:
                stront = pos.state_timestamp.strftime('%H:%M, %d %b')
            else:
                stront = getFuelValue(pos, C.STRONTIUM_CLATHRATES_TYPEID, params.displayMode)
            pos_table.append([
                pos.permalink,
                pos.custom_name,
                pos.type_id,
                pos.state,
                pos.time_until_tick,
                getFuelValue(pos, pos.fuel_type_id, params.displayMode),
                stront,
                pos.type_name,
                getFuelValue(pos, pos.fuel_type_id, 'hours_int'),
            ])
    else:
        # Since its a sorted list of tuples now it needs slightly different handling
        for _, pos, state in pos_by_timeleft[params.first_id:params.last_id]:
            if state == 3:
                stront = pos.state_timestamp.strftime('%H:%M, %d %b')
            else:
                stront = getFuelValue(pos, C.STRONTIUM_CLATHRATES_TYPEID, params.displayMode)
            pos_table.append([
                pos.permalink,
                pos.custom_name,
                pos.type_id,
                pos.state,
                pos.time_until_tick,
                getFuelValue(pos, pos.fuel_type_id, params.displayMode),
                stront,
                pos.type_name,
                getFuelValue(pos, pos.fuel_type_id, 'hours_int'),
            ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_count,  # Number of lines
        "iTotalDisplayRecords" : filtered_count,# Number of displayed lines,
        "aaData" : pos_table
    }
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
def getFuelValue(pos, fuelTypeID, displayMode):
    try:
        fuel = pos.fuel_levels.filter(type_id=fuelTypeID).latest()
        quantity = fuel.current_fuel()
        consumption = fuel.consumption
    except FuelLevel.DoesNotExist:
        quantity = 0
        consumption = 0
    if displayMode == 'quantities':
        value = print_fuel_quantity(quantity)
    else:
        if consumption == 0:
            value = '-'
        else:
            hoursLeft = int(quantity / consumption)

            if displayMode == 'hours':
                value = '%dh' % hoursLeft
            elif displayMode == 'hours_int':
                value = hoursLeft
            else:
                value = print_duration(seconds=hoursLeft * 3600, verbose=False)
    return value

