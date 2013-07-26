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

__date__ = "2012 5 10"
__author__ = "Ajurna"

from datetime import datetime, timedelta
    
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx
from django.db.models import Q
from django.db.models.aggregates import Min, Max
from django.utils.text import truncate_words
from django.utils import timezone

from ecm.utils.format import print_time_min, print_float
from ecm.utils import is_number
from ecm.utils import _json as json
from ecm.apps.common.models import UpdateDate
from ecm.apps.eve.models import Type, CelestialObject
from ecm.apps.corp.models import Corporation
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params
from ecm.plugins.accounting.models import TransactionEntry
from ecm.apps.eve import constants

DATE_PATTERN = "%Y-%m-%d"
    
    
#------------------------------------------------------------------------------
@check_user_access()
def transactions(request):
    walletID = int(request.GET.get('walletID', 0))
    entryTypeID = int(request.GET.get('entryTypeID', -1))
    entryForID = int(request.GET.get('entryForID', -1))
    amount = request.GET.get('amount',None)
    comparator = request.GET.get('comparator','>')
    
    
    from_date = TransactionEntry.objects.all().aggregate(date=Min("date"))["date"]
    if from_date is None: from_date = datetime.utcfromtimestamp(0)
    to_date = TransactionEntry.objects.all().aggregate(date=Max("date"))["date"]
    if to_date is None: to_date = timezone.now()
    
    
    wallets = [{ 'walletID' : 0, 'name' : 'All', 'selected' : walletID == 0 }]
    for w in Corporation.objects.mine().wallets.all().order_by('wallet'):
        wallets.append({
            'walletID' : w.wallet_id,
            'name' : w.name,
            'selected' : w.wallet_id == walletID
        })
    entryTypes = [{ 'refTypeID' : -1, 'refTypeName' : 'Both', 'selected' : entryTypeID == -1 }]
    for tet in TransactionEntry.TYPES:
        entryTypes.append({
            'refTypeID' : tet,
            'refTypeName' : TransactionEntry.TYPES[tet],
            'selected' : tet == entryTypeID
        })
    entryFor = [{ 'refTypeID' : -1, 'refTypeName' : 'Both', 'selected' : entryForID == -1 }]
    for ter in TransactionEntry.FOR:
        entryFor.append({
            'refTypeID' : ter,
            'refTypeName' : TransactionEntry.FOR[ter],
            'selected' : ter == entryForID
        })
    data = {
        'wallets' : wallets,
        'entryTypes' : entryTypes,
        'entryFor' : entryFor,
        'amount' : amount,
        'comparator' : comparator,
        'scan_date' : UpdateDate.get_latest(TransactionEntry),
        'from_date' : datetime.strftime(from_date, DATE_PATTERN),
        'to_date' : datetime.strftime(to_date, DATE_PATTERN),
    }
    return render_to_response("ecm/accounting/wallet_transactions.html", data, Ctx(request))


#------------------------------------------------------------------------------
journal_cols = ['date', 'type', 'price', 'quantity', 'amount', 'balance', 'location', 'wallet']
@check_user_access()
def transactions_data(request):
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.walletID    = int(REQ.get('walletID', 0))
        params.entryTypeID = int(REQ.get('entryTypeID', -1))
        params.entryForID  = int(REQ.get('entryForID', -1))
        params.amount      = request.GET.get('amount', None)
        params.comparator  = request.GET.get('comparator', 'gt')
        params.from_date   = timezone.make_aware(datetime.strptime(REQ.get('from_date', None), DATE_PATTERN), timezone.get_current_timezone())
        params.to_date     = timezone.make_aware(datetime.strptime(REQ.get('to_date', None), DATE_PATTERN), timezone.get_current_timezone())
    except:
        return HttpResponseBadRequest()
    query = TransactionEntry.objects.select_related(depth=1).all().order_by('-date')

    if params.search or params.walletID or params.entryTypeID or params.amount or (params.from_date and params.to_date):
        total_entries = query.count()
        search_args = Q()

        if params.search:
            search_args |= Q(clientName__icontains=params.search)
            station_ids = list(CelestialObject.objects.filter(itemName__icontains=params.search, group=constants.STATIONS_GROUPID).values_list('itemID', flat=True)[:100])
            item_ids = list(Type.objects.filter(typeName__icontains=params.search).values_list('typeID', flat=True)[:100])
            search_args |= Q(stationID__in=station_ids) 
            search_args |= Q(typeID__in=item_ids)
            if is_number(params.search):
                search_args |= Q(amount__gte=params.search)
        if params.walletID:
            search_args &= Q(wallet=params.walletID)
        if params.entryTypeID != -1:
            search_args &= Q(transactionType=params.entryTypeID)
        if params.entryForID != -1:
            search_args &= Q(transactionFor=params.entryForID)
        # Add query amount
        if params.amount:
            comparator_map = {
                              'gt':  Q(price__gt=params.amount), 
                              'lt':  Q(price__lt=params.amount), 
                              'gte': Q(price__gte=params.amount),
                              'lte': Q(price__lte=params.amount),
                              'eq':  Q(price=params.amount),
                              'neq': Q(price__lt=params.amount, price__gt=params.amount),
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
    
    my_corp = Corporation.objects.mine()
    
    for entry in query:
        try:
            amount = print_float(entry.journal.amount, force_sign=True)
        except AttributeError:
            amount = '0.0'
        try:
            balance = print_float(entry.journal.balance)
        except AttributeError:
            balance = ''
        
        entries.append([
            print_time_min(entry.date),
            entry.typeName,
            entry.price,
            entry.quantity,
            amount,
            balance,
            truncate_words(entry.stationName, 6),
            entry.wallet.corp_wallets.get(corp=my_corp).name,
        ])

    json_data = {
        "sEcho"                : params.sEcho,
        "iTotalRecords"        : total_entries,
        "iTotalDisplayRecords" : filtered_entries,
        "aaData"               : entries
    }

    return HttpResponse(json.dumps(json_data))