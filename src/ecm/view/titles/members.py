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

from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from ecm.view.decorators import check_user_access
from ecm.view import extract_datatable_params, get_members
from ecm.data.common.models import ColorThreshold
from ecm.data.roles.models import Title, Member


#------------------------------------------------------------------------------
@check_user_access()
def members(request, id):
    data = { 
        'title' : get_object_or_404(Title, titleID=int(id)),
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL
    }
    return render_to_response("titles/title_members.html", data, RequestContext(request))


#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def members_data(request, id):
    try:
        params = extract_datatable_params(request)
        title = Title.objects.get(titleID=int(id))
    except KeyError:
        return HttpResponseBadRequest()
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    total_members,\
    filtered_members,\
    members = get_members(query=title.members.filter(corped=True),
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

