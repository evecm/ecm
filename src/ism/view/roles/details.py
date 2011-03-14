'''
This file is part of ESM

Created on 13 mars 2011
@author: diabeteman
'''


import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest

from ism.data.roles.models import Role, RoleType, Member
from ism.data.common.models import ColorThreshold
from ism.core import utils
from ism import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from django.utils.text import truncate_words
from ism.core.utils import print_date
from ism.view.members import member_table_columns

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def role(request, role_typeName, role_id):
    try:
        type = RoleType.objects.get(typeName=role_typeName)
        role = Role.objects.get(roleType=type, roleID=int(role_id))
        role.accessLvl = role.getAccessLvl()
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    
    thresholds = list(ColorThreshold.objects.all().order_by("threshold").values("threshold", "color"))
    data = {
        'colorThresholds' : json.dumps(thresholds),
        'role_types' : RoleType.objects.all(),
        'role' : role,
        'direct_member_count' : role.members.count(),
        'total_member_count' : role.getMembersThroughTitles().count()
    }
    return render_to_response("roles/role_details.html", data, context_instance=RequestContext(request))



#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def role_data(request, role_typeName, role_id):
    try:
        iDisplayStart = int(request.GET["iDisplayStart"])
        iDisplayLength = int(request.GET["iDisplayLength"])
        sSearch = request.GET["sSearch"]
        sEcho = int(request.GET["sEcho"])
        type = RoleType.objects.get(typeName=role_typeName)
        role = Role.objects.get(roleType=type, roleID=int(role_id))
        
        try:
            column = int(request.GET["iSortCol_0"])
            ascending = (request.GET["sSortDir_0"] == "asc")
        except:
            column = 0
            ascending = True
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    except:
        return HttpResponseBadRequest()

    total_members,\
    filtered_members,\
    members = getMembers(role=role,
                         first_id=iDisplayStart, 
                         last_id=iDisplayStart + iDisplayLength - 1,
                         search_str=sSearch,
                         sort_by=member_table_columns[column], 
                         asc=ascending)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }
    
    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
def getMembers(role, first_id, last_id, search_str=None, sort_by="name", asc=True):

    sort_col = "%s_nocase" % sort_by
    
    members = role.getMembersThroughTitles(with_direct_roles=True)

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