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

__date__ = "2011 5 23"
__author__ = "diabeteman"


import json

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db.models import Q

from ecm.core.utils import print_time_min, print_float
from ecm.core.eve import db
from ecm.data.corp.models import Wallet, Corp
from ecm.data.roles.models import Member
from ecm.view.decorators import check_user_access
from ecm.view import getScanDate, extract_datatable_params
from ecm.data.accounting.models import JournalEntry, EntryType


#------------------------------------------------------------------------------
@check_user_access()
def list(request):
    walletID = int(request.GET.get('walletID', 0))
    entryTypeID = int(request.GET.get('entryTypeID', 0))

    wallets = [{ 'walletID' : 0, 'name' : 'All', 'selected' : walletID == 0 }]
    for w in Wallet.objects.all().order_by('walletID'):
        wallets.append({
            'walletID' : w.walletID,
            'name' : w.name,
            'selected' : w.walletID == walletID
        })

    entryTypes = [{ 'refTypeID' : 0, 'refTypeName' : 'All', 'selected' : entryTypeID == 0 }]
    for et in EntryType.objects.exclude(refTypeID=0).order_by('refTypeID'):
        entryTypes.append({
            'refTypeID' : et.refTypeID,
            'refTypeName' : et.refTypeName,
            'selected' : et.refTypeID == entryTypeID
        })

    data = {
        'wallets' : wallets,
        'entryTypes' : entryTypes,
        'scan_date' : getScanDate(JournalEntry)
    }
    return render_to_response("accounting/wallet_journal.html", data, RequestContext(request))




#------------------------------------------------------------------------------
journal_cols = ['wallet', 'date', 'type', 'ownerName1', 'ownerName2', 'amount', 'balance']
@check_user_access()
def list_data(request):
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.walletID = int(REQ.get('walletID', 0))
        params.entryTypeID = int(REQ.get('entryTypeID', 0))
    except:
        return HttpResponseBadRequest()

    query = JournalEntry.objects.select_related(depth=1).all().order_by('-date')

    if params.search or params.walletID or params.entryTypeID:
        total_entries = query.count()
        search_args = Q()

        if params.search:
            search_args |= Q(ownerName1__icontains=params.search)
            search_args |= Q(ownerName2__icontains=params.search)
            search_args |= Q(argName1__icontains=params.search)
            search_args |= Q(reason__icontains=params.search)
        if params.walletID:
            search_args &= Q(wallet=params.walletID)
        if params.entryTypeID:
            search_args &= Q(type=params.entryTypeID)

        query = query.filter(search_args)
        filtered_entries = query.count()
    else:
        total_entries = filtered_entries = query.count()

    query = query[params.first_id:params.last_id]
    entries = []

    # to improve performance
    try: corporationID = Corp.objects.get(id=1).corporationID
    except Corp.DoesNotExist: corporationID = 0
    members = Member.objects.all()
    other_entries = JournalEntry.objects.select_related().all()

    for entry in query:

        try: owner1 = members.get(characterID=entry.ownerID1).permalink
        except Member.DoesNotExist: owner1 = entry.ownerName1
        try: owner2 = members.get(characterID=entry.ownerID2).permalink
        except Member.DoesNotExist: owner2 = entry.ownerName2

        if entry.type_id == EntryType.BOUNTY_PRIZES:
            rats = [ str.split(':') for str in entry.reason.split(',') if ':' in str ]
            rat_list = []
            for rat_id, rat_count in rats:
                rat_list.append('%s x%s' % (db.resolveTypeName(int(rat_id))[0], rat_count))
            reason = '|'.join(rat_list)
            if reason:
                reason = (u'Killed Rats in %s|' % entry.argName1) + reason
        elif entry.type_id == EntryType.PLAYER_DONATION:
            reason = entry.reason[len('DESC: '):]
            if reason:
                reason = u'Description|' + reason
        elif entry.type_id == EntryType.CORP_WITHDRAWAL:
            reason = entry.reason[len('DESC: '):].strip('\n\t\'" ')
            reason = (u'Cash transfer by %s|' % entry.argName1) + reason
            try:
                if int(entry.ownerID1) == corporationID and int(entry.ownerID2) == corporationID:
                    related_entry = other_entries.filter(refID=entry.refID).exclude(id=entry.id)[0]
                    owner2 = related_entry.wallet.name
            except:
                pass
        else:
            reason = entry.reason

        entries.append([
            print_time_min(entry.date),
            entry.wallet.name,
            entry.type.refTypeName,
            owner1,
            owner2,
            print_float(entry.amount),
            print_float(entry.balance),
            reason,
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData" : entries
    }

    return HttpResponse(json.dumps(json_data))
