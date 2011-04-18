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

from django.template.context import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.text import truncate_words

from ecm.view import getScanDate, extract_datatable_params
from ecm.data.roles.models import Member, MemberDiff
from ecm.core.utils import print_time_min
from ecm.view.decorators import user_is_director

#------------------------------------------------------------------------------
@user_is_director()
def history(request):
    data = {
        'scan_date' : getScanDate(Member.__name__) 
    }
    return render_to_response("members/member_history.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@cache_page(60 * 60) # 1 hour cache
@user_is_director()
def history_data(request):
    try:
        extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()

    queryset = MemberDiff.objects.all().order_by('-id')
    total_members = queryset.count()

    queryset = queryset[request.first_id:request.last_id]
    members = []
    for diff in queryset:
        members.append([
            diff.new,
            diff.as_html(),
            truncate_words(diff.nickname, 5),
            print_time_min(diff.date)
        ])
    
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : total_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))

