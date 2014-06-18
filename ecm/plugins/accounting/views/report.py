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


import logging
from datetime import timedelta

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.db.models.aggregates import Sum, Avg
from django.db.models.query_utils import Q
from django.utils import timezone

from ecm.utils.tools import end_of_day, start_of_day
from ecm.plugins.accounting.models import JournalEntry, Report
from ecm.apps.corp.models import Corporation
from ecm.views.decorators import check_user_access

__date__ = '2012 04 22'
__author__ = 'tash'

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
COLUMNS_INCOME = [
     #Name               witdth type        sortable    class    
    [ 'Income', '2%', 'html', 'true', 'left' ],
    [ 'Percentage', '5%', 'string', 'true', 'right'],
    [ 'Amount', '5%', 'string', 'true', 'right'],
]

COLUMNS_EXPENDITURE = [
     #Name               witdth type        sortable    class    
    [ 'Expenditure', '2%', 'html', 'true', 'left' ],
    [ 'Percentage', '5%', 'string', 'true', 'right'],
    [ 'Amount', '5%', 'string', 'true', 'right'],
]

COLUMNS_CASHFLOW = [
     #Name               witdth type        sortable    class    
    [ 'Summary', '2%', 'html', 'true', 'left' ],
    [ 'Amount', '5%', 'string', 'true', 'right'],
]

#------------------------------------------------------------------------------
@check_user_access()
def report(request):
    # Set the period for the report to 30 days
    period = 30
    # !!!TODO: Make period variable (Datepicker)
    end = timezone.now()
    start = end - timedelta(period)
    # Get our corp ID
    corp = Corporation.objects.mine()
    corpID = corp.corporationID
    # Query all journal entries in this period
    journal_entries = JournalEntry.objects.filter(date__range=(start, end)).exclude(ownerID1__exact=corpID,ownerID2__exact=corpID)
    # Get an aggregated set of the positive income in this period
    positivie_entries = journal_entries.filter(amount__gt=0)
    # Calculate the total positive income in this period 
    income_total = positivie_entries.aggregate(Sum('amount'))['amount__sum']
    if income_total == None: income_total = 0.0
    # Calculate the sum for each journal entry type and order by entry type
    income_entries = _group_by_wallet_entry(positivie_entries)
    income_aggregated = []
    for item in income_entries:
        # populate results with percentage for each entry
        item['percentage'] = item['amount'] / (income_total / 100)
        income_aggregated.append(item)
    # Get an aggregated set of the negative_entries in this period
    negative_entries = journal_entries.filter(amount__lt=0)
    # Calculate the total expenditures in this periodamount__gt=0
    expenditure_total = negative_entries.aggregate(Sum('amount'))['amount__sum']
    if expenditure_total == None: expenditure_total = 0.0
    # Calculate the sum for each journal entry type and order by entry type
    expenditure_entries = _group_by_wallet_entry(negative_entries)
    expenditure_aggregated = []
    for item in expenditure_entries:
        item['percentage'] = item['amount'] / (expenditure_total / 100)
        expenditure_aggregated.append(item)
    # Get the daily sums for income and expenditure
    income_time = _get_daily_sums(period, positivie_entries)
    expenditure_time = _get_daily_sums(period, negative_entries)
    # Calculate the cash flow
    cashflow = income_total + expenditure_total
    # Get wallet balance
    wallet_balance = _get_wallet_balance_by_day(start, end)
    # Get custom report data
    custom_reports = _load_custom_reports()
    # Create default report data
    data = {
            'columns_income'        : COLUMNS_INCOME,
            'income_aggregated'     : income_aggregated, # aggregated
            'income_total'          : income_total, # total
            'income_time'           : income_time, # all entries in period
            'columns_expenditure'   : COLUMNS_EXPENDITURE,
            'expenditure_aggregated': expenditure_aggregated, # aggregated
            'expenditure_total'     : expenditure_total, # total
            'expenditure_time'      : expenditure_time, # all entries in period
            'columns_cashflow'      : COLUMNS_CASHFLOW,
            'cashflow'              : cashflow,
            'wallet_balance'        : wallet_balance,
            'custom_reports'        : custom_reports,
            }
    # Add custom report data
    return render_to_response("ecm/accounting/report.html", data, RequestContext(request))

def _load_custom_reports(end=timezone.now(), period=30):
    custom_reports = []
    reports = Report.objects.all()
    for report in reports:
        # Set the time period
        if report.default_period:
            start = end - timedelta(report.default_period)
        else:
            # no default period for custom report, use current period (30 days)
            start = end - timedelta(period)
            
        # Set the date range for journal entries
        entries = JournalEntry.objects.filter(date__range=(start, end))
        
        # Since entry types are many-to-many, we have to iterate over them.
        # filter(type__in) will throw an error
        search_args = Q()
        for entry_type in report.entry_types.all():
            search_args |= Q(type=entry_type)
        
        # Apply the filer    
        entries = entries.filter(search_args)
        
        # Get total sum
        custom_total = entries.aggregate(Sum('amount'))['amount__sum']
        
        # Group by wallet entry
        entries_grouped = _group_by_wallet_entry(entries)
        entries_result = []
        for entry in entries_grouped:
            entry['percentage'] = entry['amount'] / (custom_total / 100)
            entries_result.append(entry)
            
        COLUMNS_CUSTOM = [
             #Name               witdth type        sortable    class    
            [ report.name, '2%', 'html', 'true', 'left' ],
            [ 'Amount', '5%', 'string', 'true', 'right'],
        ]
        
        # Append to data
        custom_reports.append({'name': report.name, 'entries': entries_result, 'columns': COLUMNS_CUSTOM, 'total': custom_total})
    return custom_reports

#------------------------------------------------------------------------------
def _extract_date(entity):
    'extracts the starting date from an entity'
    return entity.date.date()

#------------------------------------------------------------------------------
def _get_wallet_balance_by_day(start, end):
    balances = []
    for wallet in Corporation.objects.mine().wallets.all():
        try:
            balance = JournalEntry.objects.filter(date__range=(start, end)).values('type__refTypeName').annotate(average=Avg('amount'))
        except JournalEntry.DoesNotExist:
            # no journal information, assume the balance is 0.0
            balance = 0.0
        balances.append([wallet, balance])
    return balances

#------------------------------------------------------------------------------
def _group_by_wallet_entry(query_set):
    return query_set.values('type__refTypeName').annotate(amount=Sum('amount')).order_by('type__refTypeName')

#------------------------------------------------------------------------------
def _start_date(period, start=timezone.now()):
    """
    Returns a date with a timedelta days_from_now and time 0:0:0 to mark the start of the day.
    """
    return start_of_day(start) - timedelta(period)

#------------------------------------------------------------------------------    
def _get_daily_sums(period, entries, step=1):
    """
    Returns both income and expenditure by type for each day in the provided period.
    Period is a number of days starting from utcnow back to utcnow - period.
    Step is the number of days to cummulate income and expenditure with default to 1.
    Daily sums are calculated for each day starting at 0:0:0 and ending with 23:59:59. 
    """
    start_day = _start_date(period)
    result = []
    for day in range(0, period, step):
        start = start_day + timedelta(day)
        end = end_of_day(start)
        dated_query = entries.filter(date__range=(start, end))
        entry = dated_query.aggregate(Sum('amount'))['amount__sum']
        amount = 0 if entry == None else entry
        result.append({'date':start, 'amount':amount})
    return result
