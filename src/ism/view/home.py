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

from ism.core.utils import print_time_min
from django.views.decorators.csrf import csrf_protect


#------------------------------------------------------------------------------
@login_required
@csrf_protect
def home(request):
    data = {           'memberCount' : Member.objects.filter(corped=True).count(),
               'last_member_changes' : getLastMemberChanges(),
               'role_access_changes' : getLastRoleChanges(),
              'title_access_changes' : getLastTitleChanges(),
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
        m.date = print_time_min(m.date)
        members.append(m)
    return members

#------------------------------------------------------------------------------
def getLastRoleChanges(count=10):
    roles = RoleMemberDiff.objects.all().order_by('-id')[:count]
    for r in roles:
        try:
            Member.objects.get(characterID=r.member_id)
            # if this call doesn't fail then the member exists in the database
            # we can have a link to his/her details
            r.url = "/members/%d" % r.member_id
        except:
            pass
        r.date = print_time_min(r.date)
    return roles

#------------------------------------------------------------------------------
def getLastTitleChanges(count=10):
    titles = TitleMemberDiff.objects.all().order_by('-id')[:count]
    for t in titles:
        try:
            Member.objects.get(characterID=t.member_id)
            # if this call doesn't fail then the member exists in the database
            # we can have a link to his/her details
            t.url = "/members/%d" % t.member_id
        except:
            pass
        t.date = print_time_min(t.date)
    return titles

#------------------------------------------------------------------------------
def getLastTitleCompoChanges(count=10):
    titles = TitleCompoDiff.objects.all().order_by('-id')[:count]
    for t in titles:
        t.date = print_time_min(t.date)
    return titles

