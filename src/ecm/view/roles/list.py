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

__date__ = "2011-03-02"
__author__ = "diabeteman"

import json
import httplib as http

from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, Http404

from ecm.data.roles.models import Role, RoleType
from ecm.data.common.models import ColorThreshold
from ecm.view.decorators import user_is_director
from ecm.data.corp.models import Hangar, Wallet

ROLE_TYPES = {}
for t in RoleType.objects.all(): ROLE_TYPES[t.typeName] = t.id

#------------------------------------------------------------------------------
def root(request):
    return redirect("/roles/roles")

#------------------------------------------------------------------------------
@user_is_director()
def role_type(request, role_typeName):
    try:
        role_type = RoleType.objects.get(typeName=role_typeName)
    except ObjectDoesNotExist:
        raise Http404()
    
    data = { 
        'colorThresholds' : ColorThreshold.as_json(),
        'role_types' : RoleType.objects.all(),
        'current_role_type' : role_type.typeName,
        'current_role_type_name' : role_type.dispName,
    }
    return render_to_response("roles/roles.html", data, RequestContext(request))



#------------------------------------------------------------------------------
@user_is_director()
@cache_page(3 * 60 * 60) # 3 hours cache
def role_type_data(request, role_typeName):
    try:
        role_type = RoleType.objects.get(typeName=role_typeName)
        sEcho = int(request.REQUEST["sEcho"])
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    except KeyError:
        return HttpResponseBadRequest()

    roles = []
    for role in Role.objects.filter(roleType=role_type).order_by("roleID"):
        
        members = role.members.all()
        if members.count():
            members = list(members)
            members.sort()
            members = [m.name for m in members]
            members.insert(0, "Members")
        
        titles = list(role.titles.values_list("titleName", flat=True))
        if titles: 
            titles.insert(0, "Titles")
        
        roles.append([
            role.as_html(),
            role.description,
            role.get_access_lvl(),
            role.members.count(),
            role.titles.count(),
            role.id,
            "|".join(members),
            "|".join(titles)
        ])

    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : len(roles),
        "iTotalDisplayRecords" : len(roles),
        "aaData" : roles
    }

    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@user_is_director()
def update_access_level(request):
    try:
        role_id = int(request.POST["id"])
        new_access_level = int(request.POST["value"])
        role = Role.objects.get(id=role_id)
        
        if role.hangar_id:
            # Here, the access level is related to a hangar division
            # we must modify the access level of the related hangar
            #
            # note: this will propagate the change of access level 
            #       through all roles that depend on that hangar division
            hangar = Hangar.objects.get(hangarID=role.hangar_id)
            hangar.accessLvl = new_access_level
            hangar.save()
            
        elif role.wallet_id:
            # Same as above, but with wallet divisions
            wallet = Wallet.objects.get(walletID=role.wallet_id)
            wallet.accessLvl = new_access_level
            wallet.save()
            
        elif role.roleID == 1:
            # the "director" role is specific, it is redundant in 4 role categories
            # we modify the access level of all 4 instances of the role at once
            for r in Role.objects.filter(roleID=1):
                r.accessLvl = new_access_level
                r.save()
                
        else:
            role.accessLvl = new_access_level
            role.save()
        
        return HttpResponse(content=str(new_access_level), status=http.ACCEPTED)
    except:
        return HttpResponseBadRequest()



