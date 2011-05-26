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
from ecm.core.utils import print_float
import json

__date__ = "2011 5 25"
__author__ = "diabeteman"

from datetime import datetime, timedelta

from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.view.decorators import check_user_access
from ecm.data.roles.models import Member
from ecm.data.accounting.models import JournalEntry
from ecm.view import getScanDate, extract_datatable_params




@check_user_access()
def tax_contrib(request):
    data = {
        'scan_date' : getScanDate(JournalEntry.__name__) 
    }
    return render_to_response("accounting/contrib.html", data, RequestContext(request))


columns = ['LOWER("name")', 'tax_contrib']
@check_user_access()
def tax_contrib_data(request):
    try:
        params = extract_datatable_params(request)
        if params.since == "week":
            since = datetime.utcnow() - timedelta(weeks=1)
        elif params.since == "month":
            since = datetime.utcnow() - timedelta(days=30)
        elif params.since == "year":
            since = datetime.utcnow() - timedelta(days=365)
        else:
            since = datetime.fromtimestamp(0)
    except:
        return HttpResponseBadRequest()

    contributions = member_contributions(since=since, 
                                         order_by=columns[params.column], 
                                         ascending=params.asc)
    count = len(contributions[:])
    contributions = contributions[params.first_id:params.last_id]
    
    contrib_list = []
    for c in contributions:
        contrib_list.append([
            c.permalink(),
            print_float(c.tax_contrib)
        ])
    
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : contrib_list
    }
    
    return HttpResponse(json.dumps(json_data))


MEMBER_CONTRIB_SQL = '''SELECT m."characterID" AS "characterID", m."name" AS "name", SUM(j."amount") AS "tax_contrib" 
FROM "roles_member" AS m, "accounting_journalentry" AS j 
WHERE j."type_id" IN %s 
AND j."ownerID2" = m."characterID" 
AND j."date" > %s 
AND j."date" < %s 
GROUP BY m."characterID", m."name"
ORDER BY '''
def member_contributions(since=datetime.fromtimestamp(0), until=datetime.utcnow(), 
                      types=(16,17,33,34,85), order_by="tax_contrib", ascending=False):
    
    sql = MEMBER_CONTRIB_SQL + order_by + (" ASC;" if ascending else " DESC;") 
    
    return Member.objects.raw(sql, [types, since, until])


