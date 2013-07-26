# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or # modify it under the terms of the GNU General Public License as published by
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
from django.utils import timezone
from django.contrib.auth.models import User

__date__ = "2011 5 25"
__author__ = "diabeteman"

from datetime import datetime, timedelta

from django.db.models.aggregates import Min, Max, Sum
from django.db import connection
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx
from django.utils.translation import gettext as tr

from ecm.utils import db
from ecm.utils import _json as json
from ecm.utils.format import print_float
from ecm.apps.common.models import UpdateDate
from ecm.views.decorators import check_user_access
from ecm.apps.hr.models import Member
from ecm.plugins.accounting.models import JournalEntry
from ecm.views import extract_datatable_params
from ecm.views import DATATABLES_DEFAULTS
from ecm.plugins.accounting.views import MEMBER_CONTRIB_COLUMNS, PLAYER_CONTRIB_COLUMNS, SYSTEM_CONTRIB_COLUMNS


DATE_PATTERN = "%Y-%m-%d"
OPERATION_TYPES = (
    16, # Bounty
    17, # Bounty Prize
    33, # Agent Mission Reward
    34, # Agent Mission Time Bonus Reward
    85, # Bounty Prizes
    99, # Corporate Reward Payout
    103, # Corporate Reward Tax
)

#------------------------------------------------------------------------------
@check_user_access()
def member_contrib(request):
    """
    View function URL : '/accounting/contributions/'
    """
    from_date = JournalEntry.objects.all().aggregate(date=Min("date"))["date"]
    if from_date is None: from_date = datetime.utcfromtimestamp(0)
    to_date = JournalEntry.objects.all().aggregate(date=Max("date"))["date"]
    if to_date is None: to_date = timezone.now()

    query = JournalEntry.objects.filter(type__in=OPERATION_TYPES,
                                        date__gte=from_date, date__lte=to_date)
    total_contribs = query.aggregate(sum=Sum('amount'))['sum']
    data = {
        'scan_date' : UpdateDate.get_latest(JournalEntry),
        'from_date' : datetime.strftime(from_date, DATE_PATTERN),
        'to_date' : datetime.strftime(to_date, DATE_PATTERN),
        'total_contribs' : total_contribs,
        'datatables_defaults': DATATABLES_DEFAULTS,
        'member_contrib_columns': MEMBER_CONTRIB_COLUMNS,
        'system_contrib_columns': SYSTEM_CONTRIB_COLUMNS,
        'player_contrib_columns': PLAYER_CONTRIB_COLUMNS,
        'member_ajax_url': '/accounting/contributions/members/data/',
        'system_ajax_url': '/accounting/contributions/systems/data/',
        'player_ajax_url': '/accounting/contributions/players/data/',
        'sorting': [[1,'desc']],
    }
    return render_to_response("ecm/accounting/contrib.html", data, Ctx(request))

#------------------------------------------------------------------------------
columns = ['LOWER("name")', '"tax_contrib"']
@check_user_access()
def member_contrib_data(request):
    """
    View function URL : '/accounting/contributions/members/data/'
    """
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.from_date = timezone.make_aware(datetime.strptime(REQ.get('from_date', None), DATE_PATTERN), timezone.get_current_timezone())
        to_date = datetime.strptime(REQ.get('to_date', None), DATE_PATTERN)
        if to_date.hour == 0 and to_date.minute == 0 and to_date.second == 0:
            to_date += timedelta(1)
        params.to_date = timezone.make_aware(to_date, timezone.get_current_timezone())
    except:
        return HttpResponseBadRequest()

    contributions = member_contributions(since=params.from_date,
                                         until=params.to_date,
                                         order_by=columns[params.column],
                                         ascending=params.asc)
    count = len(contributions[:])
    contributions = contributions[params.first_id:params.last_id]

    contrib_list = []
    for c in contributions:
        contrib_list.append([
            c.permalink,
            print_float(c.tax_contrib)
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : contrib_list
    }

    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
columns = ['LOWER("name")', '"tax_contrib"']
@check_user_access()
def player_contrib_data(request):
    """
    View function URL : '/accounting/contributions/players/data/'
    """
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.from_date = timezone.make_aware(datetime.strptime(REQ.get('from_date', None), DATE_PATTERN), timezone.get_current_timezone())
        to_date = datetime.strptime(REQ.get('to_date', None), DATE_PATTERN)
        if to_date.hour == 0 and to_date.minute == 0 and to_date.second == 0:
            to_date += timedelta(1)
        params.to_date = timezone.make_aware(to_date, timezone.get_current_timezone())
    except:
        return HttpResponseBadRequest()

    contributions = player_contributions(since=params.from_date,
                                         until=params.to_date,
                                         order_by=columns[params.column],
                                         ascending=params.asc)
    count = len(contributions[:])
    contributions = contributions[params.first_id:params.last_id]

    contrib_list = []
    for c in contributions:
        if c.username == None:
            contrib_list.append([
                tr('not associated'),
                print_float(c.tax_contrib)
            ])
        else:
            contrib_list.append([
                '<a href="%s" class="player">%s</a>' % (c.get_absolute_url(),c.username),
                print_float(c.tax_contrib)
            ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : contrib_list
    }

    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
def system_contrib_data(request):
    """
    View function URL : '/accounting/contributions/systems/data/'
    """
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.from_date = timezone.make_aware(datetime.strptime(REQ.get('from_date', None), DATE_PATTERN), timezone.get_current_timezone())
        to_date = datetime.strptime(REQ.get('to_date', None), DATE_PATTERN)
        if to_date.hour == 0 and to_date.minute == 0 and to_date.second == 0:
            to_date += timedelta(1)
        params.to_date = timezone.make_aware(to_date, timezone.get_current_timezone())
        # In the database query below, we use a BETWEEN operator.
        # The upper bound 'to_date' will be excluded from the interval
        # because it is a datetime with time set to 00:00 (beginning of the day).
        # We add one day in order to include the last day in the interval.
    except:
        return HttpResponseBadRequest()

    contributions = system_contributions(since=params.from_date,
                                         until=params.to_date,
                                         order_by=columns[params.column],
                                         ascending=params.asc)
    count = len(contributions)
    contributions = contributions[params.first_id:params.last_id]

    contrib_list = []
    for system, amount in contributions:
        contrib_list.append([
            '<b>%s</b>' % system,
            print_float(amount)
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : contrib_list
    }

    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
def total_contrib_data(request):
    """
    View function URL : '/accounting/contributions/total/data/'
    """
    try:
        REQ = request.GET if request.method == 'GET' else request.POST
        from_date = timezone.make_aware(datetime.strptime(REQ.get('from_date', None), DATE_PATTERN), timezone.get_current_timezone())
        to_date = timezone.make_aware(datetime.strptime(REQ.get('to_date', None), DATE_PATTERN), timezone.get_current_timezone())
    except (TypeError, KeyError, ValueError):
        from_date = JournalEntry.objects.all().aggregate(date=Min("date"))["date"]
        if from_date is None: from_date = datetime.utcfromtimestamp(0)
        to_date = JournalEntry.objects.all().aggregate(date=Max("date"))["date"]
        if to_date is None: to_date = timezone.now()

    query = JournalEntry.objects.filter(type__in=OPERATION_TYPES,
                                        date__gte=from_date, date__lte=to_date)
    total_contribs = query.aggregate(sum=Sum('amount'))['sum']

    return HttpResponse(print_float(total_contribs))


#------------------------------------------------------------------------------
MEMBER_CONTRIB_SQL = '''SELECT m."characterID" AS "characterID", m."name" AS "name", SUM(j."amount") AS "tax_contrib"
 FROM "hr_member" AS m, "accounting_journalentry" AS j
 WHERE j."type_id" IN %s
  AND j."ownerID2" = m."characterID"
  AND j."date" > %%s
  AND j."date" < %%s
 GROUP BY m."characterID", m."name"
 ORDER BY ''' % str(OPERATION_TYPES)
def member_contributions(since=datetime.utcfromtimestamp(0), until=timezone.now(),
                         order_by="tax_contrib", ascending=False):

    sql = MEMBER_CONTRIB_SQL + order_by + (" ASC;" if ascending else " DESC;")
    sql = db.fix_mysql_quotes(sql)
    return Member.objects.raw(sql, [since, until])

PLAYER_CONTRIB_SQL = '''SELECT u."username" AS "username", u."id" as "id", SUM(j."amount") AS "tax_contrib"
 FROM "accounting_journalentry" AS j left join "hr_member" AS m on (j."ownerID2" = m."characterID") left join "auth_user" u on (u."id" = m."owner_id")
 WHERE j."type_id" IN %s
  AND j."date" > %%s
  AND j."date" < %%s
 GROUP BY u."username", u."id"
 ORDER BY ''' % str(OPERATION_TYPES)
def player_contributions(since=datetime.utcfromtimestamp(0), until=timezone.now(),
                         order_by="tax_contrib", ascending=False):

    sql = PLAYER_CONTRIB_SQL + order_by + (" ASC;" if ascending else " DESC;")
    sql = db.fix_mysql_quotes(sql)
    return User.objects.raw(sql, [since, until])


#------------------------------------------------------------------------------
SYSTEM_CONTRIB_SQL = '''SELECT j."argName1" AS "argName1", SUM(j."amount") AS "tax_contrib"
 FROM "accounting_journalentry" AS j
 WHERE j."type_id" IN %s
   AND j."date" > %%s
   AND j."date" < %%s
 GROUP BY j."argName1"
 ORDER BY ''' % str(OPERATION_TYPES)
def system_contributions(since=datetime.utcfromtimestamp(0), until=timezone.now(),
                         order_by="tax_contrib", ascending=False):

    sql = SYSTEM_CONTRIB_SQL + order_by + (" ASC;" if ascending else " DESC;")
    sql = db.fix_mysql_quotes(sql)

    cursor = connection.cursor() #@UndefinedVariable
    cursor.execute(sql, [since, until])

    return cursor.fetchall()
