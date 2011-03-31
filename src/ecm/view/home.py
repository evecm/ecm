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

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from ecm.data.roles.models import MemberDiff, RoleMemberDiff, Member, TitleMemberDiff

from django.views.decorators.csrf import csrf_protect
from ecm.core import utils


#------------------------------------------------------------------------------
@login_required
@csrf_protect
def home(request):
    data = {           'memberCount' : Member.objects.filter(corped=True).count(),
               'last_member_changes' : getLastMemberChanges(),
               'last_access_changes' : getLastAccessChanges() }
    
    return render_to_response("common/home.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
def getLastMemberChanges(count=20):
    members = []
    queryset = MemberDiff.objects.all().order_by('-id')[:count]
    for m in queryset:
        try:
            Member.objects.get(characterID=m.characterID)
            # if this call doesn't fail then the member exists in the database
            # we can have a link to his/her details
            m.url = "/members/%d" % m.characterID
        except:
            pass
        m.date_str = utils.print_time_min(m.date)
        members.append(m)
    return members

#------------------------------------------------------------------------------
def getLastAccessChanges(count=20):
    roles = RoleMemberDiff.objects.all().order_by('-id')[:count]
    titles = TitleMemberDiff.objects.all().order_by('-id')[:count]
    
    changes = utils.merge_lists(roles, titles, ascending=False, attribute="date")[:count]
    
    for c in changes:
        try:
            Member.objects.get(characterID=c.member_id)
            # if this call doesn't fail then the member exists in the database
            # we can have a link to his/her details
            c.member_name = c.member.name
        except:
            c.member_name = "???"
        c.member_url = "/members/%d" % c.member_id
        c.date_str = utils.print_time_min(c.date)
        
    return changes

