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

from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext

from ecm.view.decorators import check_user_access
from ecm.view import extract_datatable_params
from ecm.data.roles.models import TitleComposition, TitleCompoDiff, Title
from ecm.core import utils
from ecm.data.common.models import ColorThreshold
from ecm.core.utils import get_access_color



#------------------------------------------------------------------------------
@check_user_access()
def details(request, id):
    
    title = get_object_or_404(Title, titleID=int(id))
    title.lastModified = TitleCompoDiff.objects.filter(title=title).order_by("-id")
    if title.lastModified:
        title.lastModified = utils.print_time_min(title.lastModified[0].date)
    else:
        title.lastModified = None
    title.color = get_access_color(title.accessLvl, ColorThreshold.objects.all().order_by("threshold"))

    data = {
        "title" : title,
        "member_count" : title.members.count(),  
        "colorThresholds" : ColorThreshold.as_json() 
    }

    return render_to_response("titles/title_details.html", data, RequestContext(request))




#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def composition_data(request, id):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    title = get_object_or_404(Title, titleID=int(id))
    query = TitleComposition.objects.filter(title=title)
    
    if params.asc: 
        query = query.order_by("role")
    else:
        query = query.order_by("-role")
    
    total_compos = query.count()
    
    query = query[params.first_id:params.last_id]
    
    compo_list = []
    for compo in query:
        compo_list.append([
            compo.role.permalink(),
            compo.role.roleType.permalink(),
            compo.role.get_access_lvl()
        ])
    
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_compos,
        "iTotalDisplayRecords" : total_compos,
        "aaData" : compo_list
    }
    
    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def compo_diff_data(request, id):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    title = get_object_or_404(Title, titleID=int(id))
    query = TitleCompoDiff.objects.filter(title=title).order_by("-date")
    total_diffs = query.count()
    
    query = query[params.first_id:params.last_id]
    
    diff_list = []
    for diff in query:
        diff_list.append([
            diff.new,
            diff.role.permalink(),
            diff.role.roleType.permalink(),
            utils.print_time_min(diff.date)
        ])
    
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_diffs,
        "iTotalDisplayRecords" : total_diffs,
        "aaData" : diff_list
    }
    
    return HttpResponse(json.dumps(json_data))
