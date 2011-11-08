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

__date__ = "2011-03-13"
__author__ = "diabeteman"

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.db.models import Q
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.text import truncate_words

from ecm.apps.hr.views import hr_ctx
from ecm.views.decorators import check_user_access
from ecm.views import getScanDate, extract_datatable_params
from ecm.apps.hr.models import Member, MemberDiff
from ecm.core import utils


#------------------------------------------------------------------------------
@check_user_access()
def history(request):
    data = {
        'scan_date' : getScanDate(Member)
    }
    return render_to_response("members/member_history.html", data, hr_ctx(request))

#------------------------------------------------------------------------------
COLUMNS = ['change', 'name', 'nickname', 'id']
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def history_data(request):
    try:
        params = extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()

    query = MemberDiff.objects.all()

    if params.column == 0 or params.column > 3:
        params.column = 3
        params.asc = False

    sort_col = COLUMNS[params.column]
    # SQL hack for making a case insensitive sort
    if params.column in (1, 2):
        sort_col = sort_col + "_nocase"
        sort_val = utils.fix_mysql_quotes('LOWER("%s")' % COLUMNS[params.column])
        query = query.extra(select={ sort_col : sort_val })

    if not params.asc: sort_col = "-" + sort_col
    query = query.extra(order_by=([sort_col]))

    if params.search:
        total_members = query.count()
        search_args = Q(name__icontains=params.search) | Q(nickname__icontains=params.search)
        query = query.filter(search_args)
        filtered_members = query.count()
    else:
        total_members = filtered_members = query.count()

    members = []
    for diff in query[params.first_id:params.last_id]:
        members.append([
            diff.new,
            diff.permalink,
            truncate_words(diff.nickname, 5),
            utils.print_time_min(diff.date)
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }

    return HttpResponse(json.dumps(json_data))

