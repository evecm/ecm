'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''


from django.shortcuts import render_to_response
from django.contrib.auth.decorators import user_passes_test
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page


from ism.core.utils import print_time_min, print_date, getAccessColor
from ism.data.roles.models import Member
from ism.core.db import resolveLocationName
from ism.data.common.models import UpdateDate
from ism import settings
from django.views.decorators.csrf import csrf_protect
from ism.core import utils


#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@csrf_protect
def list(request):
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