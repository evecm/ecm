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
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.view import getScanDate, extract_datatable_params
from ecm.data.roles.models import TitleMembership, RoleMemberDiff, TitleMemberDiff
from ecm.core import utils
from ecm.core.utils import print_time_min
from ecm.core.auth import user_is_director

#------------------------------------------------------------------------------
@user_is_director()
def access_changes(request):
    data = {
        'scan_date' : getScanDate(TitleMembership.__name__) 
    }
    return render_to_response("members/access_changes.html", data, RequestContext(request))


#------------------------------------------------------------------------------
@cache_page(60 * 60) # 1 hour cache
@user_is_director()
def access_changes_data(request):
    try:
        extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()
    
    roles = RoleMemberDiff.objects.all().order_by("-date")
    titles = TitleMemberDiff.objects.all().order_by("-date")
    
    count = roles.count() + titles.count()
    
    changes = utils.merge_lists(roles, titles, ascending=False, attribute="date")
    changes = changes[request.first_id:request.last_id]
    
    change_list = []
    for c in changes:
        change_list.append([
            c.new,
            c.member_as_html(),
            c.as_html(),
            print_time_min(c.date)
        ])
    
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : changes
    }
    
    return HttpResponse(json.dumps(json_data))
