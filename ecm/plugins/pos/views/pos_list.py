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

from django.utils.translation import ugettext_lazy as tr_lazy
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponseBadRequest
from django.db.models import Q

from ecm.utils import db
from ecm.utils import _json as json
from ecm.utils.format import print_duration
from ecm.plugins.pos.views import print_fuel_quantity
from ecm.plugins.pos.models import POS, FuelLevel
from ecm.views import extract_datatable_params, datatable_ajax_data
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
    [tr_lazy('Location'),        tr_lazy('Location'),             'moon'],
    [tr_lazy('Name'),            tr_lazy('Name'),                 'custom_name'],
    [tr_lazy('Type'),            tr_lazy('Type'),                 'type_id'],
    [tr_lazy('Status'),          tr_lazy('Status'),               'state'],
    [tr_lazy('Next Cycle'),      tr_lazy('Next Cycle'),           'online_timestamp'],
    [tr_lazy('Fuel Blocks'),     tr_lazy('Fuel Blocks'),          None],
    [tr_lazy('Strontium'),       tr_lazy('Strontium Clathrates'), None],
    [tr_lazy('Name'),            None,                   None],
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
    return render_to_response("ecm/pos/pos_list.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@cache_page(60 * 60) # 1 hour cache
@check_user_access()
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
    
    # Query all authorised by default except for superuser
    if request.user.is_superuser:
        query = POS.objects.all().select_related(depth=1)
    else:
        query = POS.objects.select_related(depth=1)
        query = query.filter(Q(authorized_groups__isnull=True) | 
                             Q(authorized_groups__in=request.user.groups.all()))
    
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
        # params.displayMode can be 'quantities', 'days', or 'hours'
        if params.displayMode == 'quantities':
            valueType = 'quantities_int'
        else:
            valueType = 'hours_int'
        
        pos_by_timeleft = []
        for pos in query:
            if params.column == 5:
                sort_val = getFuelValue(pos, pos.fuel_type_id, valueType)
            else:
                sort_val = getFuelValue(pos, C.STRONTIUM_CLATHRATES_TYPEID, valueType)
            pos_by_timeleft.append( (sort_val, pos, pos.state) )
        
        if not params.asc:
            pos_by_timeleft.sort(reverse=True)
        else:
            pos_by_timeleft.sort()
        for i, item in enumerate(pos_by_timeleft):
            if item[2] == 3: # Put reinforced at the top of the list, always
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
                pos.time_until_next_cycle,
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
                pos.time_until_next_cycle,
                getFuelValue(pos, pos.fuel_type_id, params.displayMode),
                stront,
                pos.type_name,
                getFuelValue(pos, pos.fuel_type_id, 'hours_int'),
            ])

    return datatable_ajax_data(pos_table, params.sEcho, total_count, filtered_count)

#------------------------------------------------------------------------------
def getFuelValue(pos, fuelTypeID, displayMode):
    try:
        fuel = pos.fuel_levels.filter(type_id=fuelTypeID).latest()
        quantity = fuel.current_fuel()
        consumption = fuel.consumption
    except FuelLevel.DoesNotExist:
        quantity = 0
        consumption = 0
    if consumption == 0:
        value = '-'
    elif displayMode == 'quantities_int':
        value = quantity
    elif displayMode == 'quantities':
        value = print_fuel_quantity(quantity)
    else:
        hoursLeft = int(quantity / consumption)

        if displayMode == 'hours':
            value = '%dh' % hoursLeft
        elif displayMode == 'hours_int':
            value = hoursLeft
        else: # displayMode == 'days'
            value = print_duration(seconds=hoursLeft * 3600, verbose=False)
    return value

