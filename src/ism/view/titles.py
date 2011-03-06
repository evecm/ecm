'''
This file is part of ICE Security Management

Created on 11 juil. 2010
@author: diabeteman
'''

import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.utils.text import truncate_words
from django.http import HttpResponse

from ism.data.roles.models import TitleComposition, Title, TitleCompoDiff, TitleMembership, Member
from ism.data.common.models import UpdateDate, ColorThreshold
from ism.core import utils
from ism.core.utils import print_time_min, print_date, getAccessColor
from ism import settings

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def all(request):
    colorThresholds = []
    for c in ColorThreshold.objects.all().order_by("threshold"):
        colorThresholds.append({ "threshold" : c.threshold, "color" : c.color })

    data = { 
        'scan_date' : getScanDate(), 
        'colorThresholds' : json.dumps(colorThresholds)
    }
    return render_to_response("titles.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
all_columns = [ "titleName", "accessLvl" ]
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def all_data(request):
    sEcho = int(request.GET["sEcho"])
    column = int(request.GET["iSortCol_0"])
    ascending = (request.GET["sSortDir_0"] == "asc")

    titles = getTitles(sort_by=all_columns[column], asc=ascending)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : len(titles),
        "iTotalDisplayRecords" : len(titles),
        "aaData" : titles
    }
    
    return HttpResponse(json.dumps(json_data))



#------------------------------------------------------------------------------
def getTitles(sort_by="titleID", asc=True):
    sort_col = "%s_nocase" % sort_by
    
    titlesDb = Title.objects.all().order_by("titleID")

    # SQLite hack for making a case insensitive sort
    titlesDb = titlesDb.extra(select={sort_col : "%s COLLATE NOCASE" % sort_by})
    if not asc: sort_col = "-" + sort_col
    titlesDb = titlesDb.extra(order_by=[sort_col])

    # fetch the number of members having each title
    titlesDb = titlesDb.extra(select={"title_members" : "SELECT COUNT(*) FROM roles_titlemembership, roles_member WHERE roles_titlemembership.title_id = roles_title.titleID AND roles_titlemembership.member_id = roles_member.characterID AND roles_member.corped = 1"})

    titles = []
    for t in titlesDb:
        modification_date = TitleCompoDiff.objects.filter(title=t).order_by("-id")
        if modification_date.count():
            modification_date = print_time_min(modification_date[0].date)
        else:
            modification_date = "-"

        title = [
            '<a href="/titles/%d">%s</a>' % (t.titleID, t.titleName),
            t.accessLvl,
            '<a href="/titles/%d/members">%d</a>' % (t.titleID, t.title_members),
            TitleComposition.objects.filter(title=t).count(),
            modification_date
        ]
        titles.append(title)

    return titles


#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def details(request, id):
    colorThresholds = []
    for c in ColorThreshold.objects.all().order_by("threshold"):
        colorThresholds.append({ "threshold" : c.threshold, "color" : c.color })
    
    title = Title.objects.get(titleID=int(id))
    title.lastModified = TitleCompoDiff.objects.filter(title=title).order_by("-id")
    if title.lastModified.count():
        title.lastModified = print_time_min(title.lastModified[0].date)
    else:
        title.lastModified = None
    title.color = getAccessColor(title.accessLvl, ColorThreshold.objects.all().order_by("threshold"))

    data = { "title" : title,  "colorThresholds" : json.dumps(colorThresholds) }

    return render_to_response("title_details.html", data, context_instance=RequestContext(request))




#------------------------------------------------------------------------------
composition_columns = [ "role_id" ]
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def composition_data(request, id):
    iDisplayStart = int(request.GET["iDisplayStart"])
    iDisplayLength = int(request.GET["iDisplayLength"])
    sEcho = int(request.GET["sEcho"])
    column = int(request.GET["iSortCol_0"])
    ascending = (request.GET["sSortDir_0"] == "asc")

    total_compos, composition = getTitleComposition(id=int(id),
                                                    first_id=iDisplayStart,
                                                    last_id=iDisplayStart + iDisplayLength - 1,
                                                    sort_by=composition_columns[column], 
                                                    asc=ascending)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_compos,
        "iTotalDisplayRecords" : total_compos,
        "aaData" : composition
    }
    
    return HttpResponse(json.dumps(json_data))







#------------------------------------------------------------------------------
def getTitleComposition(id, first_id, last_id, sort_by="role_id", asc=True):

    sort_col = "%s_nocase" % sort_by
    
    compos = TitleComposition.objects.filter(title=id)

    # SQLite hack for making a case insensitive sort
    compos = compos.extra(select={sort_col : "%s COLLATE NOCASE" % sort_by})
    if not asc: sort_col = "-" + sort_col
    compos = compos.extra(order_by=[sort_col])
    
    total_compos = compos.count()
    
    compos = compos[first_id:last_id]
    
    compo_list = []
    for c in compos:
        compo = [
            c.role.getDispName(),
            c.role.roleType.dispName,
            c.role.getAccessLvl()
        ] 

        compo_list.append(compo)
    
    return total_compos, compo_list



#------------------------------------------------------------------------------
diff_columns = [ "new", "role_id", "roleType", "date" ]
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def compo_diff_data(request, id):
    iDisplayStart = int(request.GET["iDisplayStart"])
    iDisplayLength = int(request.GET["iDisplayLength"])
    sEcho = int(request.GET["sEcho"])
    column = int(request.GET["iSortCol_0"])
    ascending = (request.GET["sSortDir_0"] == "asc")

    total_diffs, diffs = getTitleCompoDiff(id=int(id),
                                           first_id=iDisplayStart,
                                           last_id=iDisplayStart + iDisplayLength - 1,
                                           sort_by=diff_columns[column], 
                                           asc=ascending)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_diffs,
        "iTotalDisplayRecords" : total_diffs,
        "aaData" : diffs
    }
    
    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
def getTitleCompoDiff(id, first_id, last_id, sort_by="role_id", asc=True):

    sort_col = "%s_nocase" % sort_by
    
    diffsDb = TitleCompoDiff.objects.filter(title=id)

    # SQLite hack for making a case insensitive sort
    diffsDb = diffsDb.extra(select={sort_col : "%s COLLATE NOCASE" % sort_by})
    if not asc: sort_col = "-" + sort_col
    diffsDb = diffsDb.extra(order_by=[sort_col])
    
    total_diffs = diffsDb.count()
    
    diffsDb = diffsDb[first_id:last_id]
    
    diff_list = []
    for d in diffsDb:
        diff = [
            d.new,
            d.role.getDispName(),
            d.role.roleType.dispName,
            print_time_min(d.date)
        ] 

        diff_list.append(diff)
    
    return total_diffs, diff_list



#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def members(request, id):
    colorThresholds = []
    for c in ColorThreshold.objects.all().order_by("threshold"):
        colorThresholds.append({ "threshold" : c.threshold, "color" : c.color })

    title = Title.objects.get(titleID=int(id))

    data = { 
        'title' : title,
        'colorThresholds' : json.dumps(colorThresholds)
    }
    return render_to_response("title_members.html", data, context_instance=RequestContext(request))

members_columns = [
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
def members_data(request, id):
    iDisplayStart = int(request.GET["iDisplayStart"])
    iDisplayLength = int(request.GET["iDisplayLength"])
    sEcho = int(request.GET["sEcho"])
    column = int(request.GET["iSortCol_0"])
    ascending = (request.GET["sSortDir_0"] == "asc")

    total_members, members = getMembers(titleID=int(id),
                                        first_id=iDisplayStart, 
                                        last_id=iDisplayStart + iDisplayLength - 1,
                                        sort_by=members_columns[column], 
                                        asc=ascending)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : total_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))




#------------------------------------------------------------------------------
def getMembers(titleID, first_id, last_id, sort_by="name", asc=True):

    sort_col = "%s_nocase" % sort_by
    
    member_ids = TitleMembership.objects.filter(title=titleID).values_list("member", flat=True)

    members = Member.objects.filter(characterID__in=member_ids).filter(corped=True)

    # SQLite hack for making a case insensitive sort
    members = members.extra(select={sort_col : "%s COLLATE NOCASE" % sort_by})
    if not asc: sort_col = "-" + sort_col
    members = members.extra(order_by=[sort_col])
    
    total_members = members.count()
    
    members = members[first_id:last_id]
    
    member_list = []
    for m in members:
        memb = [
            '<a href="/members/%d">%s</a>' % (m.characterID, m.name),
            truncate_words(m.nickname, 5),
            m.accessLvl,
            m.extraRoles,
            print_date(m.corpDate),
            print_date(m.lastLogin),
            truncate_words(m.location, 5),
            m.ship
        ] 

        member_list.append(memb)
    
    return total_members, member_list

#------------------------------------------------------------------------------
def getScanDate():
    date = UpdateDate.objects.get(model_name=TitleComposition.__name__) 
    return utils.print_time_min(date.update_date)
#------------------------------------------------------------------------------
