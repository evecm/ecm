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

import json

from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.text import truncate_words

from ecm.view.decorators import check_user_access
from ecm.view import getScanDate, extract_datatable_params
from ecm.data.roles.models import Member, MemberDiff
from ecm.core.utils import print_time_min


#------------------------------------------------------------------------------
@check_user_access()
def history(request):
    data = {
        'scan_date' : getScanDate(Member.__name__) 
    }
    return render_to_response("members/member_history.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def history_data(request):
    try:
        params = extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()

    queryset = MemberDiff.objects.all().order_by('-id')
    total_members = queryset.count()

    queryset = queryset[params.first_id:params.last_id]
    members = []
    for diff in queryset:
        members.append([
            diff.new,
            diff.permalink(),
            truncate_words(diff.nickname, 5),
            print_time_min(diff.date)
        ])
    
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : total_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))

