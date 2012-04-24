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
    [ 'Summary',     '2%',  'html',     'true',     'left' ],
    [ 'Amount',          '5%',  'string',   'true',     'right'],
]

@check_user_access()
def reporting(request):
    now = datetime.now()
    start = now - timedelta(30)
    end = now
    date_entries = JournalEntry.objects.filter(date__range=(start, end))
    
    # Get an income_aggregated overview
    incomes = date_entries.filter(amount__gt=0)
    # Aggregate over type
    income_aggregated = []
    income_entries = incomes.values('type__refTypeName').annotate(amount=Sum('amount'))
    income_total = date_entries.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum']
    for item in income_entries:
        item['percentage']= item['amount'] / (income_total / 100)
        income_aggregated.append(item)
    
    # Aggregate amount for each day in period
    start_day = datetime.today() - timedelta(30)
    u = datetime.utcnow()
    start_day = datetime(u.year, u.month, u.day, 0, 0, 0, 0, u.tzinfo) - timedelta(30)
    income_time=[]
    expenditure_time=[]
    for day in range(30):
        start = start_day + timedelta(day)
        end = _end_of_day(start)
        inc_entry = JournalEntry.objects.filter(date__range=(start, end)).filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum']
        exp_entry = JournalEntry.objects.filter(date__range=(start, end)).filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum']
        amount =  0 if inc_entry == None else inc_entry
        income_time.append({'date' : start, 'amount' : amount})
        amount =  0 if exp_entry == None else exp_entry
        expenditure_time.append({'date' : start, 'amount' : amount})
        
    # Get an expenditure_aggregated overview
    expenditures = date_entries.filter(amount__lt=0)
    expenditure_entries = expenditures.values('type__refTypeName').annotate(amount=Sum('amount'))
    expenditure_total = date_entries.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum']
    expenditure_aggregated = []
    for item in expenditure_entries:
        item['percentage']= item['amount'] / (expenditure_total / 100)
        expenditure_aggregated.append(item)
        
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
            'income_aggregated'     : income_aggregated,                   # aggregated
            'income_total'          : income_total,             # total
            'income_time'           : income_time,                  # all entries in period
            'columns_expenditure'   : COLUMNS_EXPENDITURE,
            'expenditure_aggregated': expenditure_aggregated,              # aggregated
            'expenditure_total'     : expenditure_total,        # total
            'expenditure_time'      : expenditure_time,             # all entries in period
            'columns_cashflow'      : COLUMNS_CASHFLOW,
            'cashflow'              : cashflow,
            'balances'              : balances,
            }
    return render_to_response("reporting.html", data, RequestContext(request))

def extract_date(entity):
    'extracts the starting date from an entity'
    return entity.date.date()

def _end_of_day(start):
    start_of_day = datetime(start.year, start.month, start.day, 0, 0, 0, 0, start.tzinfo)
    return start_of_day + timedelta(hours = 23, minutes = 59, seconds = 59)
