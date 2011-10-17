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

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.data.corp.models import Wallet
from ecm.view.decorators import check_user_access
from ecm.view import getScanDate, extract_datatable_params
from ecm.plugins.accounting.models import JournalEntry

#------------------------------------------------------------------------------
@check_user_access()
def list(request):
    data = {
        'scan_date' : getScanDate(JournalEntry)
    }
    return render_to_response("wallets.html", data, RequestContext(request))

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
        try:
            balance = JournalEntry.objects.filter(wallet=wallet).latest().balance
        except JournalEntry.DoesNotExist:
            # no journal information, we assume the balance is 0.0
            balance = 0.0
        entries.append([
            wallet,
            balance
        ])

    if params.column == 0:
        # sort by walletID
        sort_key = lambda e: e[0].walletID
    else:
        # sort by balance
        sort_key = lambda e: e[1]

    entries.sort(key=sort_key, reverse=not params.asc)

    for wallet in entries:
        wallet[1] = wallet[0].permalink_to_journal(wallet[1])
        wallet[0] = wallet[0].name

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData" : entries
    }

    return HttpResponse(json.dumps(json_data))
