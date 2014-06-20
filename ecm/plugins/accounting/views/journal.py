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
__date__ = "2011 5 23"
__author__ = "diabeteman"

from datetime import datetime, timedelta

from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx
from django.db.models import Q
from django.db.models.aggregates import Min, Max
from django.utils import timezone

from ecm.utils.format import print_time_min, print_float
from ecm.utils import is_number
from ecm.apps.common.models import UpdateDate, ColorThreshold
from ecm.apps.eve.models import Type
from ecm.apps.corp.models import Corporation
from ecm.apps.hr.models import Member
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params, DATATABLES_DEFAULTS, datatable_ajax_data
from ecm.plugins.accounting.models import JournalEntry, EntryType
from ecm.plugins.accounting.views import WALLET_JOURNAL_COLUMNS

DATE_PATTERN = "%Y-%m-%d"

#------------------------------------------------------------------------------
@check_user_access()
def journal(request):
    walletID = int(request.GET.get('walletID', 0))
    entryTypeID = int(request.GET.get('entryTypeID', 0))
    amount = request.GET.get('amount',None)
    comparator = request.GET.get('comparator','>')
    
    from_date = JournalEntry.objects.all().aggregate(date=Min("date"))["date"]
    if from_date is None: 
        from_date = datetime.utcfromtimestamp(0)
    to_date = JournalEntry.objects.all().aggregate(date=Max("date"))["date"]
    if to_date is None: 
        to_date = timezone.now()
    
    my_corp = Corporation.objects.mine()
    
    wallets = [{ 'walletID' : 0, 'name' : 'All', 'selected' : walletID == 0 }]
    for w in my_corp.wallets.all().order_by('wallet'):
        wallets.append({
            'walletID' : w.wallet_id,
            'name' : w.name,
            'selected' : w.wallet_id == walletID
        })

    entryTypes = [{ 'refTypeID' : 0, 'refTypeName' : 'All', 'selected' : entryTypeID == 0 }]
    for et in EntryType.objects.exclude(refTypeID=0).exclude(refTypeName='').order_by('refTypeName'):
        entryTypes.append({
            'refTypeID' : et.refTypeID,
            'refTypeName' : et.refTypeName,
            'selected' : et.refTypeID == entryTypeID
        })

    data = {
        'wallets' : wallets,
        'entryTypes' : entryTypes,
        'amount' : amount,
        'comparator' : comparator,
        'scan_date' : UpdateDate.get_latest(JournalEntry),
        'from_date' : datetime.strftime(from_date, DATE_PATTERN),
        'to_date' : datetime.strftime(to_date, DATE_PATTERN),
        'datatable_defaults': DATATABLES_DEFAULTS,
        'columns': WALLET_JOURNAL_COLUMNS,
        'colorThresholds': ColorThreshold.as_json(),
        'ajax_url':'/accounting/journal/data/',
    }
    return render_to_response("ecm/accounting/wallet_journal.html", data, Ctx(request))





#------------------------------------------------------------------------------
# Database columns for ajax sorting
journal_cols = ['date', 'wallet', 'type', 'ownerName1', 'ownerName2', 'amount', 'balance']

@check_user_access()
def journal_data(request):
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.walletID = int(REQ.get('walletID', 0))
        params.entryTypeID = int(REQ.get('entryTypeID', 0))
        params.amount = request.GET.get('amount',None)
        params.comparator = request.GET.get('comparator','gt')
        params.from_date   = timezone.make_aware(datetime.strptime(REQ.get('from_date', None), DATE_PATTERN), timezone.get_current_timezone())
        params.to_date     = timezone.make_aware(datetime.strptime(REQ.get('to_date', None), DATE_PATTERN), timezone.get_current_timezone())
    except:
        return HttpResponseBadRequest()

    orderBy = journal_cols[params.column]
    if not params.asc: orderBy = "-" + orderBy    
    query = JournalEntry.objects.select_related(depth=1).all().order_by(orderBy)

    if params.search or params.walletID or params.entryTypeID or params.amount or (params.from_date and params.to_date):
        total_entries = query.count()
        search_args = Q()

        if params.search:
            search_args |= Q(ownerName1__icontains=params.search)
            search_args |= Q(ownerName2__icontains=params.search)
            search_args |= Q(argName1__icontains=params.search)
            search_args |= Q(reason__icontains=params.search)
            if is_number(params.search):
                search_args |= Q(amount__gte=params.search)
        if params.walletID:
            search_args &= Q(wallet=params.walletID)
        if params.entryTypeID:
            search_args &= Q(type=params.entryTypeID)
        # Add query amount
        if params.amount:
            comparator_map = {
                              'gt':  Q(amount__gt=params.amount), 
                              'lt':  Q(amount__lt=params.amount), 
                              'gte': Q(amount__gte=params.amount),
                              'lte': Q(amount__lte=params.amount),
                              'eq': Q(amount=params.amount),
                              'neq': Q(amount__lt=params.amount, amount__gt=params.amount),
                              }
            search_args &= comparator_map[params.comparator]
            
        # Add query dates
        if params.from_date and params.to_date:
            # + 24 hours on the to date
            search_args &= Q(date__range=(params.from_date, params.to_date + timedelta(days=1)))
            
        query = query.filter(search_args)
        filtered_entries = query.count()
    else:
        total_entries = filtered_entries = query.count()

    query = query[params.first_id:params.last_id]
    entries = []

    # to improve performance
    try: 
        corp = Corporation.objects.mine()
    except Corporation.DoesNotExist: 
        corp = Corporation(corporationID=0)
    members = Member.objects.all()
    other_entries = JournalEntry.objects.select_related().all()

    for entry in query:

        try: owner1 = members.get(characterID=entry.ownerID1).permalink
        except Member.DoesNotExist: owner1 = entry.ownerName1
        try: owner2 = members.get(characterID=entry.ownerID2).permalink
        except Member.DoesNotExist: owner2 = entry.ownerName2

        if entry.type_id == EntryType.BOUNTY_PRIZES:
            rats = [ s.split(':') for s in entry.reason.split(',') if ':' in s ]
            rat_list = []
            for rat_id, rat_count in rats:
                rat_list.append('%s x%s' % (Type.objects.get(typeID=rat_id).typeName, rat_count))
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
                if int(entry.ownerID1) == corp.corporationID and int(entry.ownerID2) == corp.corporationID:
                    related_entry = other_entries.filter(refID=entry.refID).exclude(id=entry.id)[0]
                    owner2 = related_entry.wallet.corp_wallets.get(corp=corp).name
            except:
                pass
        else:
            reason = entry.reason
        
        wallet_name = entry.wallet.corp_wallets.get(corp=corp).name
        
        entries.append([
            print_time_min(entry.date),
            wallet_name,
            entry.type.refTypeName,
            owner1,
            owner2,
            print_float(entry.amount, force_sign=True),
            print_float(entry.balance),
            reason,
        ])

    return datatable_ajax_data(entries, params.sEcho, total_entries, filtered_entries)

