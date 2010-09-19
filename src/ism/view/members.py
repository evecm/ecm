'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''


from django.shortcuts import render_to_response
from django.contrib.auth.decorators import user_passes_test, login_required
from django.template.context import RequestContext


from ism.core.utils import print_time_min, print_date, getAccessColor
from ism.data.roles.models import Member, MemberDiff
from ism.core.db import resolveLocationName
from ism.data.common.models import UpdateDate, ColorThreshold
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
            Member.objects.get(characterID=m.characterID)
            # if this call doesn't fail then the member is corped 
            # we can have a link to his/her details
            m.url = "/members/%d" % m.characterID
        except:
            pass
        m.date = print_time_min(m.date)
        members.append(m)
    members.sort(key=lambda m: m.date, reverse=True)
    return members

#------------------------------------------------------------------------------
def getMember(id):
    try:
        colorThresholds = list(ColorThreshold.objects.all().order_by("threshold"))
        member = Member.objects.get(characterID=id)
        member.corpDate = print_time_min(member.corpDate)
        member.lastLogin = print_time_min(member.lastLogin)
        member.lastLogoff = print_time_min(member.lastLogoff)
        member.location = resolveLocationName(member.locationID)
        member.base = resolveLocationName(member.baseID)
        member.color = getAccessColor(member.accessLvl)
        member.roles = member.getRoles(ignore_director=True)
        member.titles = member.getTitles()
        member.is_director = member.isDirector()
        member.title_changes = member.getTitleChanges()
    except:
        member = Member(name="No member for id: %d" % id)
    
    return member
        
#------------------------------------------------------------------------------
def getMembers():
    member_list = Member.objects.filter(corped=True)
    colorThresholds = list(ColorThreshold.objects.all().order_by("threshold"))
    for m in member_list:
        m.corpDate = print_date(m.corpDate)
        m.lastLogin = print_date(m.lastLogin)
        m.lastLogoff = print_date(m.lastLogoff)
        m.location = resolveLocationName(m.locationID)
        m.color = getAccessColor(m.accessLvl, colorThresholds)
        m.is_director = m.isDirector()
        m.extraRoles = len(m.getRoles(ignore_director=True))
        
    return member_list

#------------------------------------------------------------------------------
def getScanDate():
    date = UpdateDate.objects.get(model_name=Member.__name__) 
    return date.update_date
#------------------------------------------------------------------------------