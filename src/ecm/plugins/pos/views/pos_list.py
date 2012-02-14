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

import sys
try:
    import json
except ImportError:
    import django.utils.simplejson as json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.plugins.pos.views import print_fuel_quantity, print_duration, print_time
from ecm.plugins.pos.models import POS, FuelLevel, FuelConsumption
from ecm.views import extract_datatable_params
from ecm.views.decorators import check_user_access
from ecm.core import utils
from ecm.plugins.pos import constants as C

# This table gives the association between the status of the POS
# and the related CSS class for display
POS_CSS_STATUS = {
    0: 'pos-unanchored',
    1: 'pos-offline',
    2: 'pos-onlining',
    3: 'pos-reinforced',
    4: 'pos-online',
}

# not finished : idea to give a color to the risk of updating in the current hour.
posColorChange = {
    '1':'Green',
    '2':'Yellow',
    '3':'RedLight'
}

#------------------------------------------------------------------------------
COLUMNS = [
    # Name              Tooltip                 db_field
    ['Location',        'Location',             'moon'],
    ['Type',            'Type',                 'typeID'],
    ['Status',          'Status',               'state'],
    ['Cycle',           'Cycle Time',           'onlineTimestamp'],
    ['EU',              'Enriched Uranium',     None],
    ['O<sub>2</sub>',   'Oxygen',               None],
    ['MP',              'Mechanical Parts',     None],
    ['Cool',            'Coolant',              None],
    ['Robo.',           'Robotics',             None],
    ['LO',              'Liquid Ozone',         None],
    ['HW',              'Heavy Water',          None],
    ['Iso.',            'Isotopes',             None],
    ['Sr',              'Strontium Clathrates', None],
    ['Name',            None,                   None],
]
@check_user_access()
def all(request):
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
def all_data(request):
    '''
    Read data when table request by Ajax.
    This method takes into account search filter and segmentation table
    Read the http request (GET method handling)
    '''
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.displayMode = REQ.get('displayMode', 'quantities')
    except:
        return HttpResponseBadRequest()

    # Query all by default.
    query = POS.objects.all().select_related(depth=1)

    # Sorting
    if params.column > 3:
        params.column = 0
    sort_col = COLUMNS[params.column][2]
    # SQL hack for making a case insensitive sort
    if params.column == 1:
        sort_col = sort_col + "_nocase"
        sort_val = utils.fix_mysql_quotes('LOWER("%s")' % COLUMNS[params.column][2])
        query = query.extra(select={ sort_col : sort_val })

    if not params.asc: sort_col = "-" + sort_col
    query = query.extra(order_by=([sort_col]))

    # Then get the database content and translate to display table
    # manage the search filter
    if params.search:
        total_count = query.count()
        query = POS.objects.filter(moon__icontains=params.search)
        filtered_count = query.count()
    else:
        total_count = filtered_count = query.count()

    pos_table = []
    for pos in query[params.first_id:params.last_id]:
        # Query into Fuel table to get last values. for the current POS
        row = [
            pos.permalink,
            pos.typeID,
            pos.state,
            print_time(pos.onlineTimestamp),
            getFuelValue(pos, C.ENRICHED_URANIUM_TYPEID, params.displayMode),
            getFuelValue(pos, C.OXYGEN_TYPEID, params.displayMode),
            getFuelValue(pos, C.MECHANICAL_PARTS_TYPEID, params.displayMode),
            getFuelValue(pos, C.COOLANT_TYPEID, params.displayMode),
            getFuelValue(pos, C.ROBOTICS_TYPEID, params.displayMode),
            getFuelValue(pos, C.LIQUID_OZONE_TYPEID, params.displayMode),
            getFuelValue(pos, C.HEAVY_WATER_TYPEID, params.displayMode),
            getFuelValue(pos, pos.isotopeTypeID, params.displayMode),
            getFuelValue(pos, C.STRONTIUM_CLATHRATES_TYPEID, params.displayMode),
            pos.typeName,
        ]
        pos_table.append(row)

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
        quantity = pos.fuel_levels.filter(typeID=fuelTypeID).latest().quantity
    except FuelLevel.DoesNotExist:
        quantity = 0

    if displayMode == 'quantities':
        value = print_fuel_quantity(quantity)
    else:
        try:
            fuelCons = pos.fuel_consumptions.get(typeID=fuelTypeID)
            if fuelCons.probableConsumption == 0:
                # if "probableConsumption" is 0, we fallback to "consumption"
                consumption = fuelCons.consumption
            else:
                consumption = fuelCons.probableConsumption
        except FuelConsumption.DoesNotExist:
            consumption = sys.maxint

        if consumption == 0:
            value = '-'
        else:
            hoursLeft = int(quantity / consumption)

            if displayMode == 'hours':
                value = '%dh' % hoursLeft
            else:
                value = print_duration(hoursLeft)
    return value

