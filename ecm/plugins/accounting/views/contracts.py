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
from ecm.apps.corp.models import Corp
from django.db.models.aggregates import Count
from ecm.plugins.accounting.constants import FORMATED_CONTRACT_STATES

__date__ = '2012 04 01'
__author__ = 'tash'

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

import logging

from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext as Ctx

from ecm.apps.eve.models import BlueprintType, Type, CelestialObject
from ecm.apps.hr.models import Member
from ecm.plugins.accounting.models import Contract, ContractItem
from ecm.apps.common.models import UpdateDate
from ecm.utils.format import print_time_min, print_float, print_volume
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.views.decorators import check_user_access

LOG = logging.getLogger(__name__)

COLUMNS = [
     #Name               witdth type        sortable    class    
    [ 'Type',            '2%',  'html',     'true',         'center' ],
    [ 'Status',          "5%",  "string",   'true',         ''],
    [ 'Title',           "5%",  "string",   'false',    ''],
    [ 'Date Issued',     '5%',  'string',   'false',    ''],
    [ 'Date Expired',    '5%',  'string',   'false',    ''],
    [ 'Date Accepted',   '5%',  'string',   'false',    ''],
    [ 'Date Completed',  '5%',  'string',   'false',    ''],
    [ 'Price',           '5%',  'string',   'false',    'right' ],
    [ 'Reward',          '5%',  'string',   'false',    'right' ],
    [ 'Collateral',      '5%',  'string',   'false',    'right' ],
    [ 'Buyout',          '5%',  'string',   'false',    'right' ],
    [ 'Volume',          '5%',  'numeric',  'false',    'right' ],          
]

#------------------------------------------------------------------------------
@check_user_access()
def contracts(request):
    typeName = request.GET.get('typeName', 'All')
    statusName = request.GET.get('statusName', 'All')

    # Since we dont know the contract types, let's get them form
    # existing contracts + all option
    types = [{ 'typeName' : 'All', 'selected' : typeName == 'All'}]
    for t in Contract.objects.order_by('type').values('type').distinct():
        types.append({
                'typeName' : t['type'],
                'selected' : t['type'] == typeName
            })
    # Since we dont know the status of
    status = [{ 'statusName' : 'All', 'selected' : statusName == 'All'}]
    for t in Contract.objects.order_by('status').values('status').distinct():
        status.append({
                'statusName' : t['status'],
                'selected' : t['status'] == statusName
            })
    # Get contract types
    data = {
        'types' : types,
        'status' : status,
        'scan_date' : UpdateDate.get_latest(Contract),
        'columns' : COLUMNS,
    }
    return render_to_response('contracts.html', data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def contracts_data(request):
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.type = REQ.get('typeName', 'All')
        params.status = REQ.get('statusName', 'All')
    except:
        return HttpResponseBadRequest()

    query = Contract.objects.all() # .order_by('-dateIssued')


    if params.search or params.type or params.status:
        # Total number of entries
        total_entries = query.count()

        search_args = Q()

        if params.search:
            # Search for contract title
            search_args |= Q(title__icontains=params.search)

            # Search for contract item in the contracts
            matching_ids = [t.typeID for t in Type.objects.filter(typeName__icontains = params.search)[:100]]
            
            # HACK: Django 1.3. distincts always on the default order attribute, so we use an aggregation
            # to get unique ids
            query_items = ContractItem.objects.filter(Q(typeID__in=matching_ids)).values('contract').annotate(Count('contract'))
            for match in query_items:
                search_args |= Q(contractID=match['contract'])
                    
                
        if params.type != 'All':
            search_args &= Q(type=params.type)
        if params.status != 'All':
            search_args &= Q(status=params.status)

        query = query.filter(search_args)
        filtered_entries = query.count()
    else:
        total_entries = filtered_entries = query.count()

    query = query[params.first_id:params.last_id]
    entries = []
    for entry in query:
        entries.append([
            entry.permalink_type,
            FORMATED_CONTRACT_STATES[entry.status],
            entry.permalink,
            print_time_min(entry.dateIssued),
            print_time_min(entry.dateExpired),
            print_time_min(entry.dateAccepted),
            print_time_min(entry.dateCompleted),
            print_float(entry.price),
            print_float(entry.reward),
            print_float(entry.collateral),
            print_float(entry.buyout),
            print_volume(entry.volume)
        ])
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData" : entries,
    }
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
def details(request, contract_id):
    """
    Serves URL /accounting/contracts/<contract_id>/
    """
    try:
        contract = get_object_or_404(Contract, contractID=int(contract_id))
    except ValueError:
        raise Http404()
    issuer = _map_id(contract.issuerID)
    assignee = _map_id(contract.assigneeID)
    acceptor = _map_id(contract.acceptorID)

    try:
        startStation = CelestialObject.objects.get(itemID = contract.startStationID).itemName
    except CelestialObject.DoesNotExist:
        startStation = '???'
    try:
        endStation = CelestialObject.objects.get(itemID = contract.endStationID).itemName
    except CelestialObject.DoesNotExist:
        endStation = '???'

    # Build the data
    data = {
        'contract'     : contract,
        'issuer'       : issuer,
        'assignee'     : assignee,
        'acceptor'     : acceptor,
        'startStation' : startStation,
        'endStation'   : endStation,
    }
    return render_to_response('contract_details.html', data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def details_data(request, contract_id):
    """
    Serves URL /accounting/contracts/<contract_id>//data/
    """
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        contract_id = int(contract_id)
        params.included = REQ.get('included', 'All')
        params.singleton = REQ.get('singleton', 'All')
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    contract_items = ContractItem.objects.filter(contract=contract_id)
    total_entries = contract_items.count()
    search_args = Q()
    if params.search:
        types = _get_types(params.search)
        for type in types: #@ReservedAssignment
            search_args |= Q(typeID__exact=type.typeID)

    query = contract_items.filter(search_args)

    filtered_entries = query.count()
    if filtered_entries == None:
        total_entries = filtered_entries = query.count()

    query = query[params.first_id:params.last_id]
    entries = []
    for contract_item in query:
        entries.append([
            Type.objects.get(typeID=contract_item.typeID).typeName,
            contract_item.quantity,
            _print_rawquantity(contract_item),
            contract_item.singleton,
            _print_included(contract_item),
        ])
    return datatable_ajax_data(data=entries, echo=params.sEcho, total=total_entries, filtered=filtered_entries)

#------------------------------------------------------------------------------
def _print_rawquantity(contract_item):
    result = "---"
    raw_quantity = contract_item.rawQuantity
    if raw_quantity:
        # is bp?
        if _is_Blueprint(contract_item):
            if int(raw_quantity) == -1:
                result = "Original"
            elif int(raw_quantity) == -2:
                result = "Copy"
        # is stackable?
        elif int(raw_quantity) == -1:
            result = "non stackable"
    return result

def _print_included(contract_item):
    result = "asking"
    included = contract_item.included
    if included:
        result = "submitted"
    return result

def _is_Blueprint(contract_item):
    return BlueprintType.objects.filter(blueprintTypeID=contract_item.typeID).exists

def _get_types(typeName):
    return Type.objects.filter(typeName__icontains=typeName)

def _map_member(character_id):
    return Member.objects.get(characterID=character_id).permalink

def _map_corp(corp_id):
    return Corp.objects.get(corporationID=corp_id)

def _map_alliance(alliance_id):
    return Corp.objects.get(allianceID=alliance_id)

def _map_id(character_id):
    try:
        member = _map_member(character_id)
    except Member.DoesNotExist:
        try:
            member = _map_corp(character_id)
        except Corp.DoesNotExist:
            try:
                member = _map_alliance(character_id).allianceName
            except Corp.DoesNotExist:
                member = character_id
    return member

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]