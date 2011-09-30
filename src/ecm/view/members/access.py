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
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.view import getScanDate, extract_datatable_params
from ecm.data.roles.models import TitleMembership, RoleMemberDiff, TitleMemberDiff
from ecm.view.decorators import check_user_access
from ecm.core import utils


#------------------------------------------------------------------------------
@check_user_access()
def access_changes(request):
    data = {
        'scan_date' : getScanDate(TitleMembership)
    }
    return render_to_response("members/access_changes.html", data, RequestContext(request))


#------------------------------------------------------------------------------
COLUMNS = ['change', 'name', 'role/title', 'date']
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def access_changes_data(request):
    try:
        params = extract_datatable_params(request)
        if params.column == 1:
            lambda_sort = lambda e: e.member.name.lower()
        else:
            lambda_sort = lambda e: e.date
    except:
        return HttpResponseBadRequest()

    roles_query = RoleMemberDiff.objects.select_related(depth=1).all()
    titles_query = TitleMemberDiff.objects.select_related(depth=1).all()

    if params.search:
        total_count = roles_query.count() + titles_query.count()
        roles_search_args = Q(member__name__icontains=params.search) | Q(role__roleName__icontains=params.search)
        roles_query = roles_query.filter(roles_search_args)
        titles_search_args = Q(member__name__icontains=params.search) | Q(title__titleName__icontains=params.search)
        titles_query = titles_query.filter(titles_search_args)
        filtered_count = roles_query.count() + titles_query.count()
    else:
        total_count = filtered_count = roles_query.count() + titles_query.count()

    changes = list(roles_query) + list(titles_query)
    changes.sort(key=lambda_sort, reverse=not params.asc)
    changes = changes[params.first_id:params.last_id]

    change_list = []
    for c in changes:
        change_list.append([
            c.new,
            c.member_permalink,
            c.access_permalink,
            utils.print_time_min(c.date)
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_count,
        "iTotalDisplayRecords" : filtered_count,
        "aaData" : change_list
    }

    return HttpResponse(json.dumps(json_data))
