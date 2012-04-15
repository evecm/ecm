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
from ecm.plugins.accounting.constants import ORDER_STATES

__date__ = '2012 04 06'
__author__ = 'tash'

import logging

from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.apps.eve.models import CelestialObject, Type
from ecm.apps.hr.models import Member
from ecm.apps.common.models import UpdateDate
from ecm.plugins.accounting.models import MarketOrder
from ecm.utils.format import print_float, print_integer
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params, datatable_ajax_data

LOG = logging.getLogger(__name__)

COLUMNS = [
    # name          width   sortable    css-class
    ['Type',        '2%',   'true',     ''],
    ['Char',        '2%',   'true',     ''],
    ['Item',        '5%',   'false',    ''],
    ['Price',       '1%',   'false',    'right'],
    ['Duration',    '1%',   'false',    'right'],
    ['Station',     '5%',   'false',    ''],
    ['Vol. Ent.',   '1%',   'false',    'right'],
    ['Vol. Rem.',   '1%',   'false',    'right'],
    ['Min. Vol.',   '1%',   'false',    'right'],
    ['State',       '5%',   'false',    ''],
    ['Range',       '2%',   'false',    ''],
]

#------------------------------------------------------------------------------
@check_user_access()
def marketorders(request):
    stateID = int(request.GET.get('stateID', -1))
    typeID = request.GET.get('typeID', 0)

    states = [{
        'stateID': -1,
        'name': 'All',
        'selected' : stateID == -1 ,
    }]
    LOG.debug("stateID: %s " % stateID)
    for s in range(len(ORDER_STATES)):
        LOG.debug(s)
        states.append({
            'stateID': s,
            'name': ORDER_STATES[s],
            'selected': s == stateID,
        })

    types = [{
        'typeID': 0,
        'name': 'All',
        'selected': typeID == 0,
    }, {
        'typeID': 1,
        'name': 'Buy Order',
        'selected': typeID == 1,
    }, {
        'typeID': 2,
        'name': 'Sell Order',
        'selected': typeID == 2
    }]

    data = {
        'states': states,
        'types': types,
        'columns': COLUMNS,
        'scan_date': UpdateDate.get_latest(MarketOrder),
    }
    return render_to_response('marketorders.html', data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def marketorders_data(request):
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.stateID = int(REQ.get('stateID', -1))
        params.typeID = int(REQ.get('typeID', 0))
    except:
        return HttpResponseBadRequest()

    query = MarketOrder.objects.all() # .order_by('-dateIssued')
    total_entries = query.count()
    search_args = Q()
    if params.search:
        types = _get_types(params.search)
        for type in types: #@ReservedAssignment
            search_args |= Q(typeID__exact=type.typeID)

    if params.stateID > -1:
        # States
        state = params.stateID
        search_args &= Q(orderState=state)
    
    # Types
    if params.typeID == 1:
        search_args &= Q(bid=True)
    elif params.typeID == 2:
        search_args &= Q(bid=False)

    query = query.filter(search_args)
    filtered_entries = query.count()
    if filtered_entries == None:
        total_entries = filtered_entries = query.count()

    query = query[params.first_id:params.last_id]
    entries = []

    for entry in query:
        # Get the Type Name from Type
        eve_type = Type.objects.get(typeID=entry.typeID)

        # Get the owner of the order
        try: owner = Member.objects.get(characterID=entry.charID).permalink
        except Member.DoesNotExist: owner = entry.charID

        # Build the entry list
        entries.append([
            _map_type(entry.bid),
            #entry.charID,
            owner,
            eve_type.typeName,
            print_float(entry.price),
            '%d days' % entry.duration,
            CelestialObject.objects.get(itemID=entry.stationID).itemName,
            print_integer(entry.volEntered),
            print_integer(entry.volRemaining),
            print_integer(entry.minVolume),
            '%s' % ORDER_STATES[entry.orderState],
            _map_range(entry)
        ])

    return datatable_ajax_data(entries, params.sEcho, total_entries, filtered_entries)

#------------------------------------------------------------------------------
def _map_type(bid):
    result = ''
    if bid:
        result = 'Buy Order'
    else:
        result = 'Sell Order'
    return result

#------------------------------------------------------------------------------
_range_map = {-1: 'Station', 32767: 'Region'}
def _map_range(market_order):
    # check if it is a buy order
    if market_order.bid:
        return _range_map.get(int(market_order.range), '%d Jumps' % market_order.range)
    else:
        # Sell orders are bound to station
        return _range_map.get(-1)

#------------------------------------------------------------------------------
def _get_types(typeName):
    return Type.objects.filter(typeName__icontains=typeName)

