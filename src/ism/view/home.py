'''
This file is part of ICE Security Management

Created on 3 fev. 2010
@author: diabeteman
'''

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from ism.data.roles.models import MemberDiff, RoleMemberDiff, TitleCompoDiff, Member,\
    TitleMemberDiff

from ism.core.utils import print_time_min, merge_lists
from django.views.decorators.csrf import csrf_protect


#------------------------------------------------------------------------------
@login_required
@csrf_protect
def home(request):
    data = {           'memberCount' : Member.objects.filter(corped=True).count(),
               'last_member_changes' : getLastMemberChanges(),
               'last_access_changes' : getLastAccessChanges(),
          'last_title_compo_changes' : getLastTitleCompoChanges() }
    
    return render_to_response("home.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
def getLastMemberChanges(count=20):
    members = []
    queryset = list(MemberDiff.objects.all().order_by('-id'))[:count]
    for m in queryset:
        try:
            Member.objects.get(characterID=m.characterID)
            # if this call doesn't fail then the member exists in the database
            # we can have a link to his/her details
            m.url = "/members/%d" % m.characterID
        except:
            pass
        m.date_str = print_time_min(m.date)
        members.append(m)
    return members

#------------------------------------------------------------------------------
def getLastAccessChanges(count=20):
    roles = list(RoleMemberDiff.objects.all().order_by('-id')[:count])
    titles = list(TitleMemberDiff.objects.all().order_by('-id')[:count])
    
    changes = merge_lists(roles, titles, "date")[:count]
    
    for c in changes:
        try:
            Member.objects.get(characterID=c.member_id)
            # if this call doesn't fail then the member exists in the database
            # we can have a link to his/her details
            c.url = "/members/%d" % c.member_id
        except:
            pass
        c.date_str = print_time_min(c.date)
        
    return changes

#------------------------------------------------------------------------------
def getLastTitleCompoChanges(count=10):
    titles = TitleCompoDiff.objects.all().order_by('-id')[:count]
    for t in titles:
        t.date_str = print_time_min(t.date)
    return titles

