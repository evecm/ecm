'''
This file is part of ICE Security Management

Created on 11 juil. 2010
@author: diabeteman
'''

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_protect

from ism.data.roles.models import TitleComposition, Role, Title
from ism.data.corp.models import Hangar, Wallet
from ism.data.common.models import UpdateDate
from ism.core import image, utils
from ism import settings
from ism.core.utils import getAccessColor

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@csrf_protect
def titles(request):
    data = {  'title_list' : getTitles(),
              'role_list' : getRoles(),
                'scan_date' : getScanDate(),
            }
    return render_to_response("titles.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
def getTitles():
    titlesDb = Title.objects.all().order_by("titleID")
    titles = []
    colorThresholds = list(ColorThreshold.objects.all().order_by("threshold"))
    class T: pass
    for t in titlesDb:
        title = T()
        title.name = t.titleName
        title.icon = image.getImage(t.titleName)
        title.roles = [ tc.role_id for tc in TitleComposition.objects.filter(title=t) ]
        title.accessLvl = t.accessLvl   
        title.color = getAccessColor(t.accessLvl, colorThresholds)
        titles.append(title)
    
    return titles

#------------------------------------------------------------------------------
def getRoles():
    rolesDb = Role.objects.all().order_by("id")
    class R: pass
    roles = []
    for r in rolesDb:
        if r.roleID == 1: continue # we don't want directors here
        if r.roleType_id in (2,4,6,8): continue # don't want grantable roles neither
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
    
#------------------------------------------------------------------------------
def getScanDate():
    date = UpdateDate.objects.get(model_name=TitleComposition.__name__) 
    return date.update_date
#------------------------------------------------------------------------------