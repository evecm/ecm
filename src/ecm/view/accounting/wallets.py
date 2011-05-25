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

__date__ = "2011 5 25"
__author__ = "diabeteman"

import json

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.core.utils import print_float
from ecm.data.corp.models import Wallet
from ecm.view.decorators import check_user_access
from ecm.view import getScanDate, extract_datatable_params
from ecm.data.accounting.models import JournalEntry

#------------------------------------------------------------------------------
@check_user_access()
def list(request):
    data = {
        'scan_date' : getScanDate(JournalEntry.__name__) 
    }
    return render_to_response("accounting/wallets.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
def list_data(request):
    try:
        params = extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()

    query = Wallet.objects.all()
    total_entries = filtered_entries = query.count()

    entries = []
    for wallet in query:
        entries.append([
            wallet,
            JournalEntry.objects.filter(wallet=wallet).order_by("-date")[0].balance
        ])
    
    if params.column == 0:
        # sort by walletID
        sort_key = lambda e: e[0].walletID
    else:
        # sort by balance
        sort_key = lambda e: e[1]
    
    entries.sort(key=sort_key, reverse=not params.asc)
    
    for wallet in entries:
        wallet[0] = wallet[0].permalink()
        wallet[1] = print_float(wallet[1])
    
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData" : entries
    }
    
    return HttpResponse(json.dumps(json_data))
