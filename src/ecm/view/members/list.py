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

__date__ = "2010-05-16"
__author__ = "diabeteman"

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.apps.hr.models import Member
from ecm.view.decorators import check_user_access
from ecm.apps.common.models import ColorThreshold
from ecm.view import getScanDate, get_members, extract_datatable_params



#------------------------------------------------------------------------------
@check_user_access()
def all(request):
    data = { 
        'scan_date' : getScanDate(Member), 
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL
    }
    return render_to_response("members/member_list.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def all_data(request):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    total_members,\
    filtered_members,\
    members = get_members(query=Member.objects.filter(corped=True),
                          first_id=params.first_id, 
                          last_id=params.last_id,
                          search_str=params.search,
                          sort_by=params.column, 
                          asc=params.asc)
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
def unassociated(request):
    data = { 
        'scan_date' : getScanDate(Member), 
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL
    }
    return render_to_response("members/unassociated.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def unassociated_data(request):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    total_members,\
    filtered_members,\
    members = get_members(query=Member.objects.filter(corped=True, owner=None),
                          first_id=params.first_id, 
                          last_id=params.last_id,
                          search_str=params.search,
                          sort_by=params.column, 
                          asc=params.asc)
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def unassociated_clip(request):
    query = Member.objects.filter(corped=True, owner=None).order_by("name")
    data = query.values_list("name", flat=True)
    return HttpResponse("\n".join(data))
