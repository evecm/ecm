'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''

import json

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.template.context import RequestContext
from django.http import HttpResponse
from django.utils.text import truncate_words
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q

from ism.core.utils import print_time_min, print_date, getAccessColor
from ism.data.roles.models import Member, MemberDiff, RoleMemberDiff, TitleMemberDiff
from ism.core.db import resolveLocationName
from ism.data.common.models import UpdateDate, ColorThreshold
from ism import settings
from ism.core import utils

columns = [
    "name",
    "nickname",
    "accessLvl",
    "extraRoles",
    "corpDate",
    "lastLogin",
    "location",
    "ship"
]

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def all(request):
    colorThresholds = []
    for c in ColorThreshold.objects.all().order_by("threshold"):
        colorThresholds.append({ "threshold" : c.threshold, "color" : c.color })

    data = { 
        'scan_date' : getScanDate(), 
        'colorThresholds' : json.dumps(colorThresholds)
    }
    return render_to_response("member_list.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def all_data(request):
    try:
        iDisplayStart = int(request.GET["iDisplayStart"])
        iDisplayLength = int(request.GET["iDisplayLength"])
        sSearch = request.GET["sSearch"]
        sEcho = int(request.GET["sEcho"])
        try:
            column = int(request.GET["iSortCol_0"])
            ascending = (request.GET["sSortDir_0"] == "asc")
        except:
            column = 0
            ascending = True
    except:
        pass

    total_members,\
    filtered_members,\
    members = getMembers(first_id=iDisplayStart, 
                         last_id=iDisplayStart + iDisplayLength - 1,
                         search_str=sSearch,
                         sort_by=columns[column], 
                         asc=ascending)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def details(request, characterID):
    
    member = getMember(int(characterID))
    
    if member.corped:
        member.date = getScanDate()
    else:
        d = MemberDiff.objects.filter(characterID=member.characterID, new=False).order_by("-id")[0]
        member.date = utils.print_time_min(d.date)
    
    data = { 'member' : member }
    return render_to_response("member_details.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def history(request):
    data = {
        'scan_date' : getScanDate() 
    }
    return render_to_response("member_history.html", data, context_instance=RequestContext(request))


#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def history_data(request):
    iDisplayStart = int(request.GET["iDisplayStart"])
    iDisplayLength = int(request.GET["iDisplayLength"])
    sEcho = int(request.GET["sEcho"])

    total_members, members = getLastMembers(first_id=iDisplayStart, 
                                            last_id=iDisplayStart + iDisplayLength - 1)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : total_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def access_changes(request):
    data = {
        'scan_date' : getScanDate() 
    }
    return render_to_response("access_changes.html", data, context_instance=RequestContext(request))


#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def access_changes_data(request):
    iDisplayStart = int(request.GET["iDisplayStart"])
    iDisplayLength = int(request.GET["iDisplayLength"])
    sEcho = int(request.GET["sEcho"])

    count, changes = getAccessChanges(first_id=iDisplayStart, 
                                      last_id=iDisplayStart + iDisplayLength - 1)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : changes
    }
    
    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def access_changes_member_data(request, characterID):
    iDisplayStart = int(request.GET["iDisplayStart"])
    iDisplayLength = int(request.GET["iDisplayLength"])
    sEcho = int(request.GET["sEcho"])

    count, changes = getMemberAccessChanges(characterID=int(characterID),
                                            first_id=iDisplayStart, 
                                            last_id=iDisplayStart + iDisplayLength - 1)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : changes
    }
    
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
def getLastMembers(first_id, last_id):
    queryset = MemberDiff.objects.all().order_by('-id')
    total_members = queryset.count()

    queryset = queryset[first_id:last_id]
    members = []
    for m in queryset:
        try:
            Member.objects.get(characterID=m.characterID)
            # if this call doesn't fail then we can have a link to his/her details
            name = '<a href="/members/%d">%s</a>' % (m.characterID, m.name)
        except:
            name = '<b>%s</b>' % m.name

        members.append([
            m.new,
            name,
            truncate_words(m.nickname, 5),
            print_time_min(m.date)
        ])
    
    return total_members, members

#------------------------------------------------------------------------------
def getMember(id):
    try:
        colorThresholds = ColorThreshold.objects.all().order_by("threshold")
        member = Member.objects.get(characterID=id)
        member.corpDate = print_time_min(member.corpDate)
        member.lastLogin = print_time_min(member.lastLogin)
        member.lastLogoff = print_time_min(member.lastLogoff)
        member.base = resolveLocationName(member.baseID)
        member.color = getAccessColor(member.accessLvl, colorThresholds)
        member.roles = member.getRoles(ignore_director=True)
        member.titles = member.getTitles()
        member.is_director = member.isDirector()
        member.title_changes = member.getTitleChanges()
    except:
        member = Member(name="No member for id: %d" % id)
    
    return member
        
#------------------------------------------------------------------------------
def getMembers(first_id, last_id, search_str=None, sort_by="name", asc=True):

    sort_col = "%s_nocase" % sort_by
    
    members = Member.objects.filter(corped=True)

    # SQLite hack for making a case insensitive sort
    members = members.extra(select={sort_col : "%s COLLATE NOCASE" % sort_by})
    if not asc: sort_col = "-" + sort_col
    members = members.extra(order_by=[sort_col])
    
    if search_str:
        total_members = members.count()
        search_args = Q(name__icontains=search_str) | Q(nickname__icontains=search_str)
        
        if "DIRECTOR".startswith(search_str.upper()):
            search_args = search_args | Q(accessLvl=Member.DIRECTOR_ACCESS_LVL)
        
        members = members.filter(search_args)
        filtered_members = members.count()
    else:
        total_members = filtered_members = members.count()
    
    members = members[first_id:last_id]
    
    member_list = []
    for m in members:
        titles = ["Titles"]
        titles.extend([ str(t) for t in m.getTitles() ])
        if m.extraRoles: 
            roles = [ str(r) for r in m.getRoles(ignore_director=True) ]
            if len(roles): roles.insert(0, "Roles")
        else:
            roles = []
        memb = [
            '<a href="/members/%d">%s</a>' % (m.characterID, m.name),
            truncate_words(m.nickname, 5),
            m.accessLvl,
            m.extraRoles,
            print_date(m.corpDate),
            print_date(m.lastLogin),
            truncate_words(m.location, 5),
            m.ship,
            "|".join(titles),
            "|".join(roles)
        ] 

        member_list.append(memb)
    
    return total_members, filtered_members, member_list

#------------------------------------------------------------------------------
def getAccessChanges(first_id, last_id):
    
    roles = RoleMemberDiff.objects.all().order_by("-id")
    titles = TitleMemberDiff.objects.all().order_by("-id")
    
    count = roles.count() + titles.count()
    
    changes = utils.merge_lists(list(roles), list(titles), "date")
    changes = changes[first_id:last_id]
    
    change_list = []
    for c in changes:
        try:
            access = '<a href="/titles/%d">%s</a>' % (c.title_id, unicode(c.title)) 
        except AttributeError:
            access = '<a href="/roles/%d">%s</a>' % (c.role_id, unicode(c.role))
        
        change = [
            c.new,
            '<a href="/members/%d">%s</a>' % (c.member.characterID, c.member.name),
            access,
            print_time_min(c.date)
        ]

        change_list.append(change)
    
    return count, change_list


#------------------------------------------------------------------------------
def getMemberAccessChanges(characterID, first_id, last_id):
    
    roles = RoleMemberDiff.objects.filter(member=characterID).order_by("-id")
    titles = TitleMemberDiff.objects.filter(member=characterID).order_by("-id")
    
    count = roles.count() + titles.count()
    
    changes = utils.merge_lists(roles, titles, "date")
    changes = changes[first_id:last_id]
    
    change_list = []
    for c in changes:
        try:
            access = '<a href="/titles/%d">%s</a>' % (c.title_id, unicode(c.title)) 
        except AttributeError:
            access = '<a href="/roles/%d">%s</a>' % (c.role_id, unicode(c.role))
        
        change = [
            c.new,
            access,
            print_time_min(c.date)
        ] 

        change_list.append(change)
    
    return count, change_list



#------------------------------------------------------------------------------
def getScanDate():
    date = UpdateDate.objects.get(model_name=Member.__name__) 
    return utils.print_time_min(date.update_date)
#------------------------------------------------------------------------------
