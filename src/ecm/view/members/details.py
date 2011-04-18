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
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

from ecm.core import utils
from ecm.data.roles.models import MemberDiff, Member, RoleMemberDiff, TitleMemberDiff
from ecm.view import getScanDate, extract_datatable_params
from ecm.data.common.models import ColorThreshold
from ecm.core.utils import print_time_min, get_access_color
from ecm.core.db import resolveLocationName
from ecm.view.decorators import user_owns_character


#------------------------------------------------------------------------------
@user_owns_character()
def details(request, characterID):
    try:
        colorThresholds = ColorThreshold.objects.all().order_by("threshold")
        member = Member.objects.get(characterID=int(characterID))
        member.corpDate = print_time_min(member.corpDate)
        member.lastLogin = print_time_min(member.lastLogin)
        member.lastLogoff = print_time_min(member.lastLogoff)
        member.base = resolveLocationName(member.baseID)
        member.color = get_access_color(member.accessLvl, colorThresholds)
        member.roles_no_director = member.roles.exclude(roleID=1) # exclude 'director'
        member.all_titles = member.titles.all()
        member.is_director = member.is_director()
        
        if member.corped:
            member.date = getScanDate(Member.__name__)
        else:
            d = MemberDiff.objects.filter(characterID=member.characterID, new=False).order_by("-id")[0]
            member.date = utils.print_time_min(d.date)
    except ObjectDoesNotExist:
        member = Member(characterID=int(characterID), name="???")
    
    data = { 'member' : member }
    return render_to_response("members/member_details.html", data, RequestContext(request))


#------------------------------------------------------------------------------
@cache_page(60 * 60) # 1 hour cache
@user_owns_character()
def access_changes_member_data(request, characterID):
    try:
        extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()
    
    roles = RoleMemberDiff.objects.filter(member=characterID).order_by("-id")
    titles = TitleMemberDiff.objects.filter(member=characterID).order_by("-id")
    
    count = roles.count() + titles.count()
    
    changes = utils.merge_lists(roles, titles, ascending=False, attribute="date")
    changes = changes[request.first_id:request.last_id]
    
    change_list = []
    for change in changes:
        change_list.append([
            change.new,
            change.access_as_html(),
            print_time_min(change.date)
        ])
    
    json_data = {
        "sEcho" : request.sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : change_list
    }
    
    return HttpResponse(json.dumps(json_data))
