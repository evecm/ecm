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
    # name          width   sortable    css-class   type
    ['Type',        '2%',   'true',     '',         'html' ],
    ['Char',        '2%',   'true',     '',         'html' ],
    ['Item',        '5%',   'true',     '',         'string' ],
    ['Price',       '1%',   'true',     'right',    'html'],
    ['Total',       '3%',   'true',     'right',    'html'],
    ['Duration',    '1%',   'false',    'right',    'numeric'],
    ['Station',     '5%',   'false',    '',         'string' ],
    ['Vol. Ent.',   '1%',   'false',    'right',    'numeric'],
    ['Vol. Rem.',   '1%',   'false',    'right',    'numeric'],
    ['Min. Vol.',   '1%',   'false',    'right',    'numeric'],
    ['State',       '5%',   'false',    '',         'string' ],
    ['Range',       '2%',   'false',    '',         'string' ],
]

SORT_COLUMNS= {
    0: 'bid',
    1: 'charID',
    2: 'typeID',
    3: 'price',         
}

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
    for sid, name in MarketOrder.STATE.items():
        states.append({
            'stateID': sid,
            'name': name,
            'selected': name == stateID,
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
    return render_to_response('ecm/accounting/marketorders.html', data, Ctx(request))

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
    
    # Apply sorting (if desc, set '-' in front of the column to sort)
    
    query = query.order_by(_get_sort_order(params))
    
    query = query[params.first_id:params.last_id]
    entries = []
    page_total = 0 # The total sell order sum for the current page (params.first_id:params.last_id)
    for entry in query:
        # Get the Type Name from Type
        eve_type = Type.objects.get(typeID=entry.typeID)

        # Get the owner of the order
        try: 
            owner = Member.objects.get(characterID=entry.charID).permalink
        except Member.DoesNotExist: 
            owner = entry.charID

        try:
            station = CelestialObject.objects.get(itemID=entry.stationID).itemName
        except CelestialObject.DoesNotExist:
            station = str(entry.stationID)
        
        page_total += entry.price * entry.volRemaining
        
        # Build the entry list
        entries.append([
            entry.get_type,
            #entry.charID,
            owner,
            eve_type.typeName,
            print_float(entry.price),
            print_float(entry.price * entry.volRemaining),
            '%d days' % entry.duration,
            station,
            print_integer(entry.volEntered),
            print_integer(entry.volRemaining),
            print_integer(entry.minVolume),
            entry.state_html,
            entry.map_range
        ])
    
    return datatable_ajax_data(entries, params.sEcho, total_entries, filtered_entries)

#------------------------------------------------------------------------------
def _get_types(typeName):
    return Type.objects.filter(typeName__icontains=typeName)

#------------------------------------------------------------------------------
def _get_sort_order(params):
    sort_string = SORT_COLUMNS[params.column] if params.asc else "-%s" % (SORT_COLUMNS[params.column])
    return sort_string
