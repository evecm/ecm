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

__date__ = "2011 5 25"
__author__ = "diabeteman"


from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.utils import _json as json
from ecm.plugins.accounting.views import wallet_journal_permalink, WALLET_LINK
from ecm.apps.common.models import UpdateDate
from ecm.apps.corp.models import Corporation
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params
from ecm.utils.format import print_float
from ecm.plugins.accounting.models import JournalEntry

#------------------------------------------------------------------------------
@check_user_access()
def wallets(request):
    data = {
        'scan_date' : UpdateDate.get_latest(JournalEntry)
    }
    return render_to_response("ecm/accounting/wallets.html", data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def wallets_data(request):
    try:
        params = extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()
    
    my_corp = Corporation.objects.mine()
    
    query = my_corp.wallets.all()
    total_entries = filtered_entries = query.count()

    entries = []
    for wallet in query:
        try:
            balance = JournalEntry.objects.filter(wallet=wallet.wallet).latest().balance
        except JournalEntry.DoesNotExist:
            # no journal information, we assume the balance is 0.0
            balance = 0.0
        entries.append([
            wallet,
            balance
        ])

    if params.column == 0:
        # sort by walletID
        sort_key = lambda e: e[0].wallet.walletID
    else:
        # sort by balance
        sort_key = lambda e: e[1]

    entries.sort(key=sort_key, reverse=not params.asc)
    total_balance = 0
    for wallet in entries:
        total_balance += wallet[1]
        wallet[1] = wallet_journal_permalink(wallet[0], wallet[1])
        wallet[0] = wallet[0].name
        
    # Append total amount
    value = WALLET_LINK % ("/accounting/journal/",
                          "Click to access this wallet's journal", print_float(total_balance))
    entries.append(['<b>Total</b>', "<b>%s</b>" % value])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData" : entries,
    }

    return HttpResponse(json.dumps(json_data))
