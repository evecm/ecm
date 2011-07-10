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
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.data.roles.models import TitleComposition, TitleCompoDiff
from ecm.view.decorators import check_user_access
from ecm.view import getScanDate, extract_datatable_params
from ecm.core.utils import print_time_min




#------------------------------------------------------------------------------
@check_user_access()
def changes(request):
    data = {
        'scan_date' : getScanDate(TitleComposition) 
    }
    return render_to_response("titles/changes.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@cache_page(60 * 60) # 1 hour cache
@check_user_access()
def changes_data(request):
    try:
        params = extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()

    titles = TitleCompoDiff.objects.all().order_by("-date")
    
    count = titles.count()
    
    changes = titles[params.first_id:params.last_id]
    
    change_list = []
    for c in changes:
        change_list.append([
            c.new,
            c.title.permalink(),
            c.role.permalink(),
            print_time_min(c.date)
        ])
    
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : change_list
    }
    
    return HttpResponse(json.dumps(json_data))
