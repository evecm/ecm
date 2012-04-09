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


try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

import logging
from django.db.models import Q
from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.conf import settings

from ecm.apps.eve.models import BlueprintType, Type, CelestialObject
from ecm.apps.hr.models import Member
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext as Ctx
from ecm.plugins.accounting.models import Contract, ContractItem
from ecm.utils.format import print_time_min, print_float, print_volume
from ecm.views import getScanDate, extract_datatable_params, datatable_ajax_data
from ecm.views.decorators import check_user_access

LOG = logging.getLogger(__name__)

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
        'scan_date' : getScanDate(Contract)
    }
    return render_to_response('contracts.html', data, Ctx(request))

#------------------------------------------------------------------------------
TYPE_LINK = '<img src="%s" alt="%s" name="%s" class="contracttype">'
def _type_perma_link(entry):
    lower_type = str(entry.type).lower()
    return TYPE_LINK % ('%saccounting/img/%s.png' % (settings.STATIC_URL, lower_type),
                        entry.type, entry.type)
    
TITLE_LINK = '<a href="%s" class="contract">%s</a>'
def _title_perma_link(entry):
    url = '/accounting/contracts/%d/' % entry.contractID
    if entry.title == "" :
        title = "&lt;No Title&gt;"
    else:
        title = entry.title    
    
    return TITLE_LINK % (url, title)
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

    query = Contract.objects.select_related(depth=1).all() # .order_by('-dateIssued')
    query_items = ContractItem.objects.all()
    
    
    if params.search or params.type or params.status:
        # Total number of entries
        total_entries = query.count()

        search_args = Q()

        if params.search:
            # Search for contract title
            search_args |= Q(title__icontains=params.search)
            # Search for contract item in the contracts
            types = _get_types(params.search).values('typeID')
#            for type in types: #@ReservedAssignment
            matching_items = query_items.filter(typeID=types[0]['typeID'])
            for item in matching_items:
                LOG.error(item.contract)
                search_args |= Q(contractID=item.contract)    
            #    search_args |= Q(contractID__exact=item.typeName)
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
            _type_perma_link(entry),
            entry.status,
            _title_perma_link(entry),
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
    
    
    try: issuer = Member.objects.get(characterID=contract.issuerID).permalink
    except Member.DoesNotExist: issuer = contract.issuerID
    
    try: assignee = Member.objects.get(characterID=contract.assigneeID).permalink
    except Member.DoesNotExist: assignee = contract.assigneeID
    
    try: acceptor = Member.objects.get(characterID=contract.acceptorID).permalink
    except Member.DoesNotExist: acceptor = contract.acceptorID
    
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
