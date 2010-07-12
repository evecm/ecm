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
from ism.core import image

@login_required
@csrf_protect
def titles(request):
    data = {  'member_list' : getTitles(),
                'scan_date' : getScanDate(),
            }
    return render_to_response("memberlist.html", data, context_instance=RequestContext(request))
 
 
 
 
def getTitles():
    titlesDb = Title.objects.all().order_by("titleID")
    titles = {}
    class T: pass
    for t in titlesDb:
        title = T()
        title.name = t.titleName
        title.icon = image.getImage(t.titleName)
        titles[t.titleID] = title
    
    titleCompoDb = TitleComposition.objects.all().order_by("title_id")
    class TC: pass
    for tcdb in titleCompoDb:
        tc = TC()
        tc.
    
    
    
    rolesDb = Role.objects.all().order_by("id")
    class R:
        pass
    
    for r in rolesDb:
        if r.roleID == 1: continue # we don't want directors here
        role = R()
        role.name = r.displayName
        if r.hangar_id :
            role.name = role.name % Hangar.objects.get(hangarID=r.hangar_id).name
        if r.wallet_id : 
            role.name = role.name % Wallet.objects.get(walletID=r.wallet_id).name
        role.accessLvl = r.getAccessLvl()
        
     
    
def getScanDate():
    date = UpdateDate.objects.get(model_name=TitleComposition.__name__) 
    return date.update_date