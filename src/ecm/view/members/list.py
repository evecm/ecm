# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-05-16"
__author__ = "diabeteman"

import json

from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.data.roles.models import Member
from ecm.view.decorators import check_user_access
from ecm.data.common.models import ColorThreshold
from ecm.view import getScanDate, get_members, extract_datatable_params



#------------------------------------------------------------------------------
@check_user_access()
def all(request):
    data = { 
        'scan_date' : getScanDate(Member.__name__), 
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL
    }
    return render_to_response("members/member_list.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def all_data(request):
    try:
        extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    total_members,\
    filtered_members,\
    members = get_members(query=Member.objects.filter(corped=True),
                          first_id=request.first_id, 
                          last_id=request.last_id,
                          search_str=request.search,
                          sort_by=request.column, 
                          asc=request.asc)
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
def unassociated(request):
    data = { 
        'scan_date' : getScanDate(Member.__name__), 
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL
    }
    return render_to_response("members/unassociated.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def unassociated_data(request):
    try:
        extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    total_members,\
    filtered_members,\
    members = get_members(query=Member.objects.filter(corped=True, ownership=None),
                          first_id=request.first_id, 
                          last_id=request.last_id,
                          search_str=request.search,
                          sort_by=request.column, 
                          asc=request.asc)
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def unassociated_clip(request):
    query = Member.objects.filter(corped=True, ownership=None).order_by("name")
    data = query.values_list("name", flat=True)
    return HttpResponse("\n".join(data))
