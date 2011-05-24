# Copyright (c) 2010-2011 Robin Jarry
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
from ecm.core.utils import print_time_min, print_quantity, print_float
from ecm.data.roles.models import Member

__date__ = "2011 5 23"
__author__ = "diabeteman"


import json

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db.models import Q

from ecm.view.decorators import check_user_access
from ecm.view import getScanDate, extract_datatable_params
from ecm.data.accounting.models import JournalEntry


#------------------------------------------------------------------------------
@check_user_access()
def list(request):
    data = {
        'scan_date' : getScanDate(JournalEntry.__name__) 
    }
    return render_to_response("accounting/wallet_journal.html", data, RequestContext(request))




#------------------------------------------------------------------------------
journal_cols = ['wallet', 'date', 'type', 'ownerName1', 'ownerName2', 'amount', 'balance']
@check_user_access()
def list_data(request):
    params = extract_datatable_params(request)
    params.walletID = int(request.GET.get('walletID', 0))
    params.entryTypeID = int(request.GET.get('entryTypeID', 0))

    query = JournalEntry.objects.all().order_by('-date')

    if params.search or params.walletID or params.entryTypeID:
        total_entries = query.count()
        search_args = Q()
        
        if params.search:
            search_args |= Q(ownerName1__icontains=params.search) 
            search_args |= Q(ownerName2__icontains=params.search)
            search_args |= Q(argName1__icontains=params.search)
            search_args |= Q(reason__icontains=params.search)
        if params.walletID:
            search_args |= Q(wallet=params.walletID)
        if params.entryTypeID:
            search_args |= Q(type=params.entryTypeID)
        
        query = query.filter(search_args)
        filtered_entries = query.count()
    else:
        total_entries = filtered_entries = query.count()

    query = query[params.first_id:params.last_id]
    entries = []
    for entry in query:
        try:
            owner1 = Member.objects.get(characterID=entry.ownerID1).as_html()
        except Member.DoesNotExist:
            owner1 = entry.ownerName1
        try:
            owner2 = Member.objects.get(characterID=entry.ownerID2).as_html()
        except Member.DoesNotExist:
            owner2 = entry.ownerName2
        entries.append([
            print_time_min(entry.date),
            entry.wallet.permalink(),
            entry.type.refTypeName,
            owner1,
            owner2,
            print_float(entry.amount),
            print_float(entry.balance),
        ])
    
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData" : entries
    }
    
    return HttpResponse(json.dumps(json_data))