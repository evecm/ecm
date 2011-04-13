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
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest

from ecm.data.roles.models import TitleComposition, TitleCompoDiff
from ecm.view import getScanDate
from ecm.core.utils import print_time_min
from ecm.core.auth import user_is_director



#------------------------------------------------------------------------------
@user_is_director()
def changes(request):
    data = {
        'scan_date' : getScanDate(TitleComposition.__name__) 
    }
    return render_to_response("titles/changes.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@cache_page(60 * 60 * 15) # 1 hour cache
@user_is_director()
def changes_data(request):
    try:
        iDisplayStart = int(request.GET["iDisplayStart"])
        iDisplayLength = int(request.GET["iDisplayLength"])
        sEcho = int(request.GET["sEcho"])
    except:
        return HttpResponseBadRequest()

    count, changes = getTitleChanges(first_id=iDisplayStart, 
                                     last_id=iDisplayStart + iDisplayLength - 1)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : changes
    }
    
    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
def getTitleChanges(first_id, last_id):
    
    titles = TitleCompoDiff.objects.all().order_by("-date")
    
    count = titles.count()
    
    changes = titles[first_id:last_id]
    
    change_list = []
    for c in changes:
        change = [
            c.new,
            '<a href="/titles/%d" class="title">%s</a>' % (c.title_id, unicode(c.title)),
            '<a href="/roles/%d/%d" class="role">%s</a>' % (c.role.roleType.id, c.role_id, unicode(c.role)),
            print_time_min(c.date)
        ]

        change_list.append(change)
    
    return count, change_list