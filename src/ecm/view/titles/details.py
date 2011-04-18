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

from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext

from ecm.view import extract_datatable_params
from ecm.data.roles.models import TitleComposition, TitleCompoDiff, Title
from ecm.core import utils
from ecm.data.common.models import ColorThreshold
from ecm.core.utils import get_access_color
from ecm.view.decorators import user_is_director


#------------------------------------------------------------------------------
@cache_page(3 * 60 * 60) # 3 hours cache
@user_is_director()
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
@cache_page(3 * 60 * 60) # 3 hours cache
@user_is_director()
def composition_data(request, id):
    try:
        extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    title = get_object_or_404(Title, titleID=int(id))
    query = TitleComposition.objects.filter(title=title)
    
    if request.asc: 
        query = query.order_by("role")
    else:
        query = query.order_by("-role")
    
    total_compos = query.count()
    
    query = query[request.first_id:request.last_id]
    
    compo_list = []
    for compo in query:
        compo_list.append([
            compo.role.as_html(),
            compo.role.roleType.as_html(),
            compo.role.get_access_lvl()
        ])
    
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : total_compos,
        "iTotalDisplayRecords" : total_compos,
        "aaData" : compo_list
    }
    
    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
@cache_page(3 * 60 * 60) # 3 hours cache
@user_is_director()
def compo_diff_data(request, id):
    try:
        extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    title = get_object_or_404(Title, titleID=int(id))
    query = TitleCompoDiff.objects.filter(title=title).order_by("-date")
    total_diffs = query.count()
    
    query = query[request.first_id:request.last_id]
    
    diff_list = []
    for diff in query:
        diff_list.append([
            diff.new,
            diff.role.as_html(),
            diff.role.roleType.as_html(),
            utils.print_time_min(diff.date)
        ])
    
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : total_diffs,
        "iTotalDisplayRecords" : total_diffs,
        "aaData" : diff_list
    }
    
    return HttpResponse(json.dumps(json_data))
