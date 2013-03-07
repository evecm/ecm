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

__date__ = '2012 04 01'
__author__ = 'tash'

import logging

from django.db.models import Q
from django.http import HttpResponseBadRequest, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext as Ctx
from django.db.models.aggregates import Count, Sum

from ecm.apps.corp.models import Corporation, Alliance
from ecm.plugins.accounting.constants import REPACKAGED_VOLUMES
from ecm.apps.eve.models import BlueprintType, Type, CelestialObject
from ecm.apps.hr.models import Member
from ecm.plugins.accounting.models import Contract, ContractItem
from ecm.apps.common.models import UpdateDate
from ecm.utils.format import print_date, print_float, print_volume, print_integer
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.views.decorators import check_user_access

LOG = logging.getLogger(__name__)

COLUMNS = [
     #Name               witdth type        sortable    class    
    [ 'Type',            '2%',  'html',     'false',     'center' ],
    [ 'Status',          "5%",  "string",   'false',     ''],
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
TYPES = [ (0, 'All') ] + Contract.TYPE.items() 
STATUSES = [ (0, 'All') ] + Contract.STATUS.items() 
@check_user_access()
def contracts(request):
    
    _type = request.GET.get('type', 0) # default to All
    _status = request.GET.get('status', 0) # default to All
    
    # Get contract types
    data = {
        'types': [ (ID, name, ID == _type) for ID, name in TYPES ],
        'statuses': [ (ID, name, ID == _status) for ID, name in STATUSES ],
        'scan_date': UpdateDate.get_latest(Contract),
        'columns': COLUMNS,
    }
    return render_to_response('ecm/accounting/contracts.html', data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def contracts_data(request):
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.type = int(REQ.get('type', 0)) # default to All
        params.status = int(REQ.get('status', 0)) # default to All
    except (ValueError, KeyError):
        return HttpResponseBadRequest()

    query = Contract.objects.all()

    total_entries = query.count()
    if params.search or params.type or params.status:
        search_args = Q()

        if params.search:
            # Search for contract title
            search_args |= Q(title__icontains=params.search)

            # Search for contract item in the contracts
            matching_ids = [t.typeID for t in Type.objects.filter(typeName__icontains=params.search)[:100]]
            
            # HACK: Django 1.3. distincts always on the default order attribute, so we use an aggregation
            # to get unique ids
            query_items = ContractItem.objects.filter(Q(typeID__in=matching_ids)).values('contract').annotate(Count('contract'))
            for match in query_items:
                search_args |= Q(contractID=match['contract'])
                    
        if params.type:     
            search_args &= Q(type=params.type)
        if params.status:
            search_args &= Q(status=params.status)

        query = query.filter(search_args)
    
    filtered_entries = query.count()
    
    entries = []
    for entry in query[params.first_id:params.last_id]:
        entries.append([
            entry.permalink_type,
            entry.status_html,
            entry.permalink,
            print_date(entry.dateIssued),
            print_date(entry.dateExpired),
            print_date(entry.dateAccepted),
            print_date(entry.dateCompleted),
            print_float(entry.price),
            print_float(entry.reward),
            print_float(entry.collateral),
            print_float(entry.buyout),
            print_volume(entry.volume, rounded=True),
        ])

    return datatable_ajax_data(entries, params.sEcho, total_entries, filtered_entries)

#------------------------------------------------------------------------------
DETAILS_COLUMNS = [
     #Name                  witdth type        sortable    class    
    [ 'Type',                       '35%', 'html',     'false',    'left' ],
    #[ 'Category / Group',           '5%',  'string',   'false',    'left'],
    [ 'Quantity',                   '5%',  'string',   'false',    'right'],
    [ 'Volume each',                '25%', 'string',   'false',    'right'],
    [ 'Volume total',               '25%', 'string',   'false',    'right'],
    #[ 'Raw Quantity',               '5%',  'string',   'false',    'center'],
    [ 'Included',                   '5%',  'string',   'false',    'right' ],
]
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
        startStation = CelestialObject.objects.get(itemID=contract.startStationID).itemName
    except CelestialObject.DoesNotExist:
        startStation = str(contract.startStationID)
    try:
        endStation = CelestialObject.objects.get(itemID=contract.endStationID).itemName
    except CelestialObject.DoesNotExist:
        endStation = str(contract.endStationID)

    # Build the data
    data = {
        'contract'     : contract,
        'issuer'       : issuer,
        'assignee'     : assignee,
        'acceptor'     : acceptor,
        'startStation' : startStation,
        'endStation'   : endStation,
        'columns'      : DETAILS_COLUMNS,
        'grouped'      : 0,
    }
    return render_to_response('ecm/accounting/contract_details.html', data, Ctx(request))

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
        params.grouped = int(REQ.get('grouped', 0))
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

   
    entries = []
    if params.grouped:
        item_group = query.values('typeID', 'rawQuantity', 'singleton', 'included').annotate(quantity=Sum('quantity'))
        total_entries = item_group.count() 
        filtered_entries = total_entries
        for item in item_group[params.first_id:params.last_id]:
            item_type = Type.objects.get(typeID=item['typeID'])
            #cat_group = "%s / %s" % ( item_type.category.categoryName,item_type.group.groupName)
            entries.append([
                item_type.typeName,
                #cat_group,
                print_integer(item['quantity']),
                _print_repackaged_volume(item_type),
                _print_repackaged_volume(item_type, item['quantity']),
                #_print_rawquantity(item['rawQuantity'], item['typeID']),
                _print_included(item['included']),
            ]) 
    else:
        query = query[params.first_id:params.last_id]
        for contract_item in query:
            item_type = Type.objects.get(typeID=contract_item.typeID)
            #cat_group = "%s / %s" % ( item_type.category.categoryName,item_type.group.groupName)
            entries.append([
                item_type.typeName,
                #cat_group,
                print_integer(contract_item.quantity),
                _print_repackaged_volume(item_type),
                _print_repackaged_volume(item_type, contract_item.quantity),
                #_print_rawquantity(contract_item.rawQuantity, contract_item.typeID),
                _print_included(contract_item.included),
            ])
    return datatable_ajax_data(data=entries, echo=params.sEcho, total=total_entries, filtered=filtered_entries)

#------------------------------------------------------------------------------
def _print_rawquantity(raw_quantity, type_id):
    result = "---"
    if raw_quantity:
        # is bp?
        if _is_Blueprint(type_id):
            if int(raw_quantity) == -1:
                result = "Original"
            elif int(raw_quantity) == -2:
                result = "Copy"
        # is stackable?
        elif int(raw_quantity) == -1:
            result = "non stackable"
    return result

def _print_included(included):
    return "submitted" if included else "asking"

def _print_repackaged_volume(item, quantity=1):
    result = ""
    if REPACKAGED_VOLUMES.has_key(item.group.groupName):
        vol_rep = print_volume(REPACKAGED_VOLUMES[item.group.groupName] * quantity, rounded=True)
        vol_tot = print_volume(item.volume * quantity, rounded=True)
        result = "%s / %s" % ( vol_rep, vol_tot)
    else:
        vol = print_volume(item.volume * quantity, rounded=True)
        result = "%s / %s" % (vol, vol)
    return result

def _is_Blueprint(type_id):
    return BlueprintType.objects.filter(blueprintTypeID=type_id).exists

def _get_types(typeName):
    return Type.objects.filter(typeName__icontains=typeName)

def _map_member(character_id):
    return Member.objects.get(characterID=character_id).permalink

def _map_corp(corp_id):
    return Corporation.objects.get(corporationID=corp_id)

def _map_alliance(alliance_id):
    return Alliance.objects.get(allianceID=alliance_id)

def _map_id(character_id):
    try:
        member = _map_member(character_id)
    except Member.DoesNotExist:
        try:
            member = _map_corp(character_id)
        except Corporation.DoesNotExist:
            try:
                member = _map_alliance(character_id).name
            except Alliance.DoesNotExist:
                member = character_id
    return member
