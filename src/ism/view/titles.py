'''
This file is part of ICE Security Management

Created on 11 juil. 2010
@author: diabeteman
'''

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from ism.settings import MEDIA_URL
from ism.data.roles.models import TitleComposition, Role, Title
from ism.data.corp.models import Hangar, Wallet
from ism.data.common.models import UpdateDate
from ism.core import image

@login_required
@csrf_protect
def titles(request):
    data = {  'title_list' : getTitles(),
              'role_list' : getRoles(),
                'scan_date' : getScanDate(),
            }
    return render_to_response("titles.html", data, context_instance=RequestContext(request))




def getTitles():
    titlesDb = Title.objects.all().order_by("titleID")
    titles = []
    class T: pass
    for t in titlesDb:
        title = T()
        title.name = t.titleName
        title.icon = image.getImage(t.titleName)
        title.roles = [ tc.role_id for tc in TitleComposition.objects.filter(title=t) ]
        titles.append(title)
    
    return titles
    
def getRoles():
    rolesDb = Role.objects.all().order_by("id")
    class R: pass
    roles = []
    for r in rolesDb:
        if r.roleID == 1: continue # we don't want directors here
        role = R()
        role.id = r.id
        role.name = r.dispName
        role.description = r.description
        if r.hangar_id :
            role.name = role.name % Hangar.objects.get(hangarID=r.hangar_id).name
        if r.wallet_id : 
            role.name = role.name % Wallet.objects.get(walletID=r.wallet_id).name
        role.accessLvl = r.getAccessLvl()
        roles.append(role)
        
    return roles
    
    
def getScanDate():
    date = UpdateDate.objects.get(model_name=TitleComposition.__name__) 
    return date.update_date