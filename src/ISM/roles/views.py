'''
This file is part of ICE Security Management

Created on 01 fev. 2010
@author: diabeteman
'''

from ISM.roles.models import Title, Role, RoleType
from django.shortcuts import render_to_response

grantableRoles = (2,4,6,8)


def titles(request):
    types = []
    titles = [ ttl for ttl in Title.objects.all() ]
    
    for t in RoleType.objects.all() :
        if t.id in grantableRoles : continue
        ty = _Type()
        ty.name = t.dispName
        ty.roles = []
        for r in Role.objects.filter(roleType=t) :
            if r.roleID == 1 : continue
            ro = _Role()
            if r.hangar :
                ro.name = r.dispName % r.hangar.name
            elif r.wallet :
                ro.name = r.dispName % r.wallet.name
            else :
                ro.name = r.dispName
            
            ro.titles = [ tt['titleID'] for tt in r.titles.values() ]
            ty.roles.append(ro)
        types.append(ty)
        
    return render_to_response("titles.html", {'corp_titles' : titles,
                                              'types'       : types, 
                                              'title'       : 'Titles'})

def titleDetails(request, title_id):
    return render_to_response("base.html", {'page_title' : title_id,'title_id' : title_id})




class _Type():
    pass

class _Role():
    pass

class _Title():
    pass

