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

__date__ = "2010-02-03"
__author__ = "diabeteman"

import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.data.roles.models import MemberDiff, RoleMemberDiff, Member, TitleMemberDiff
from ecm.data.common.models import ColorThreshold
from ecm.view.decorators import user_has_titles
from ecm.core import utils

#------------------------------------------------------------------------------
@user_has_titles()
def home(request):
    data = {
        'last_member_changes' : getLastMemberChanges(),
        'last_access_changes' : getLastAccessChanges(),
        'distribution' : access_lvl_distribution(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL 
    }
    
    return render_to_response("common/home.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
def getLastMemberChanges(count=20):
    members = MemberDiff.objects.all().order_by('-id')[:count]
    for m in members:
        m.date_str = utils.print_time_min(m.date)
    return members

#------------------------------------------------------------------------------
def getLastAccessChanges(count=20):
    roles = RoleMemberDiff.objects.all().order_by('-id')[:count]
    titles = TitleMemberDiff.objects.all().order_by('-id')[:count]
    
    changes = utils.merge_lists(roles, titles, ascending=False, attribute="date")[:count]
    
    for c in changes:
        c.date_str = utils.print_time_min(c.date)
        
    return changes

#------------------------------------------------------------------------------
def access_lvl_distribution():
    thresholds = ColorThreshold.objects.all().order_by("threshold")
    for th in thresholds: th.members = 0
    members = Member.objects.filter(corped=True).order_by("accessLvl")
    levels = members.values_list("accessLvl", flat=True)
    i = 0
    for level in levels:
        if level > thresholds[i].threshold:
            i += 1
        thresholds[i].members += 1
    
    distribution_json = []
    
    for th in thresholds:
        distribution_json.append({
            "threshold" : th.threshold,
            "members" : th.members,
            "color" : th.color
        })
    
    return json.dumps(distribution_json)