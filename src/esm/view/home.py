'''
This file is part of ICE Security Management

Created on 3 fev. 2010
@author: diabeteman
'''

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from esm.data.roles.models import MemberDiff, RoleMemberDiff, Member, TitleMemberDiff

from django.views.decorators.csrf import csrf_protect
from esm.core import utils


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

