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

__date__ = "2011-03-13"
__author__ = "diabeteman"


import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.core.exceptions import ObjectDoesNotExist

from ecm.view import extract_datatable_params, get_members
from ecm.data.roles.models import Role, RoleType, Member
from ecm.data.common.models import ColorThreshold
from ecm.view.decorators import user_is_director

#------------------------------------------------------------------------------
@user_is_director()
def role(request, role_typeName, role_id):
    try:
        type = RoleType.objects.get(typeName=role_typeName)
        role = Role.objects.get(roleType=type, roleID=int(role_id))
        role.accessLvl = role.get_access_lvl()
    except ObjectDoesNotExist:
        raise Http404()
    
    data = {
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL,
        'role_types' : RoleType.objects.all(),
        'role' : role,
        'direct_member_count' : role.members.count(),
        'total_member_count' : role.members_through_titles().count()
    }
    return render_to_response("roles/role_details.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@user_is_director()
@cache_page(3 * 60 * 60) # 3 hours cache
def role_data(request, role_typeName, role_id):
    try:
        extract_datatable_params(request)
        type = RoleType.objects.get(typeName=role_typeName)
        role = Role.objects.get(roleType=type, roleID=int(role_id))
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    except:
        return HttpResponseBadRequest()

    total_members,\
    filtered_members,\
    members = get_members(query=role.members_through_titles(with_direct_roles=True),
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
