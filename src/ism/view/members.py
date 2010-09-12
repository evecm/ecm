'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''


from django.shortcuts import render_to_response
from django.contrib.auth.decorators import user_passes_test, login_required
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page


from ism.core.utils import print_time_min, print_date, getAccessColor
from ism.data.roles.models import Member, MemberDiff
from ism.core.db import resolveLocationName
from ism.data.common.models import UpdateDate
from ism import settings
from django.views.decorators.csrf import csrf_protect
from ism.core import utils


#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@csrf_protect
def all(request):
    data = {  'member_list' : getMembers(),
                'scan_date' : getScanDate(),
            }
    return render_to_response("memberlist.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@csrf_protect
def details(request, characterID):
    data = {  
        'member' : getMember(int(characterID)),
        'scan_date' : getScanDate() 
    }
    return render_to_response("memberdetails.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@login_required
@csrf_protect
def history(request):
    
    try:    since_id = int(request.GET["since_id"])
    except: since_id = -1
    
    members = getLastMembers(since_id)
    last_id = members[0].id
    first_id = members[-1].id
    
    data = {
        'member_list' : members,
        'last_id' : last_id,
        'first_id' : first_id,
        'scan_date' : getScanDate() 
    }
    return render_to_response("memberhistory.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
def getLastMembers(since_id, count=100):
    members = []
    
    if since_id != -1:
        queryset = list(MemberDiff.objects.filter(id__lt=since_id).order_by('-id'))[:count]
    else:
        queryset = list(MemberDiff.objects.all().order_by('-id'))[:count]
    for m in queryset:
        try:
            memb = Member.objects.get(characterID=m.characterID)
            m.url = "/members/%d/" % m.characterID
            m.date = print_time_min(m.date)
        except:
            m.date = print_time_min(m.date)
        members.append(m)
    members.sort(key=lambda m: m.date, reverse=True)
    return members

#------------------------------------------------------------------------------
def getMember(id):
    try:
        member = Member.objects.get(characterID=id)
    except:
        member = Member(name="No member for id: %d" % id)
    member.corpDate = print_time_min(member.corpDate)
    member.lastLogin = print_time_min(member.lastLogin)
    member.lastLogoff = print_time_min(member.lastLogoff)
    member.location = resolveLocationName(member.locationID)
    member.base = resolveLocationName(member.baseID)
    member.color = getAccessColor(member.accessLvl)
    member.roles = member.getRoles()
    member.titles = member.getTitles()
    member.is_director = 1 in [role.id for role in member.roles]
    
    return member
        
#------------------------------------------------------------------------------
def getMembers():
    member_list = Member.objects.all()
    for m in member_list:
        m.corpDate = print_date(m.corpDate)
        m.lastLogin = print_date(m.lastLogin)
        m.lastLogoff = print_date(m.lastLogoff)
        m.location = resolveLocationName(m.locationID)
        m.color = getAccessColor(m.accessLvl)
        roles = m.getRoles()
        m.is_director = 1 in [role.id for role in roles]
        m.extraRoles = len(roles)
        
    return member_list

#------------------------------------------------------------------------------
def getScanDate():
    date = UpdateDate.objects.get(model_name=Member.__name__) 
    return date.update_date
#------------------------------------------------------------------------------