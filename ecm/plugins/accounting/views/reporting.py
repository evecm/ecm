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
from datetime import timedelta
from django.shortcuts import render_to_response
from django.utils.datetime_safe import datetime
from ecm.views.decorators import check_user_access
from django.template.context import RequestContext
import logging
from ecm.plugins.accounting.models import JournalEntry
from django.db.models.aggregates import Sum, Avg
from ecm.apps.corp.models import Wallet

__date__ = '2012 04 22'
__author__ = 'tash'

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json
    

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
COLUMNS_INCOME = [
     #Name               witdth type        sortable    class    
    [ 'Income',     '2%',  'html',     'true',     'left' ],
    [ 'Percentage',               '5%',  'string',   'true',     'right'],
    [ 'Amount',          '5%',  'string',   'true',     'right'],
]

COLUMNS_EXPENDITURE = [
     #Name               witdth type        sortable    class    
    [ 'Expenditure',     '2%',  'html',     'true',     'left' ],
    [ 'Percentage',               '5%',  'string',   'true',     'right'],
    [ 'Amount',          '5%',  'string',   'true',     'right'],
]

COLUMNS_CASHFLOW = [
     #Name               witdth type        sortable    class    
    [ 'Cash Flow',     '2%',  'html',     'true',     'left' ],
    [ 'Amount',          '5%',  'string',   'true',     'right'],
]

@check_user_access()
def reporting(request):
    now = datetime.now()
    start = now - timedelta(30)
    end = now
    date_entries = JournalEntry.objects.filter(date__range=(start, end))
    
    # Get an income overview
    income_entries = date_entries.filter(amount__gt=0).values('type__refTypeName').annotate(amount=Sum('amount'))
    income_total = date_entries.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum']
    income = []
    for item in income_entries:
        item['percentage']= item['amount'] / (income_total / 100)
        income.append(item)
        
    # Get an expenditure overview
    expenditure_entries = date_entries.filter(amount__lt=0).values('type__refTypeName').annotate(amount=Sum('amount'))
    expenditure_total = date_entries.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum']
    expenditure = []
    for item in expenditure_entries:
        item['percentage']= item['amount'] / (expenditure_total / 100)
        expenditure.append(item)
    # Get a cash flow overview
    cashflow = income_total + expenditure_total
    
    # Get wallet balance
    wallets = Wallet.objects.all()
    balances = []
    for wallet in wallets:
        try:
            balance = JournalEntry.objects.filter(date__range=(start, end)).values('type__refTypeName').annotate(average=Avg('amount'))
        except JournalEntry.DoesNotExist:
            # no journal information, we assume the balance is 0.0
            balance = 0.0
        balances.append([
            wallet,
            balance,
        ]) 
    data = {
            'columns_income'        : COLUMNS_INCOME,
            'income'                : income,
            'income_total'          : income_total,
            'columns_expenditure'   : COLUMNS_EXPENDITURE,
            'expenditure'           : expenditure,
            'expenditure_total'     : expenditure_total,
            'columns_cashflow'      : COLUMNS_CASHFLOW,
            'cashflow'              : cashflow,
            'balances'              : balances,
            }
    return render_to_response("reporting.html", data, RequestContext(request))
