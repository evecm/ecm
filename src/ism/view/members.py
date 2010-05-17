'''
This file is part of ICE Security Management

Created on 16 mai 2010
@author: diabeteman
'''


from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.views.decorators.cache import cache_page
from django.db.models.aggregates import Max


from ism.core.utils import limit_text_size, print_date, print_time
from ism.data.roles.models import Member, MemberDiff
from ism.core.db import resolveLocationName
from ism.data.common.models import UpdateDate



@login_required
@cache_page(60 * 15) # 15 minutes cache
def list(request):
    data = {  'member_list' : getMembers(),
                'scan_date' : getScanDate(),
            }
    return render_to_response("memberlist.html", data, context_instance=RequestContext(request))

def getMembers():
    member_list = Member.objects.all()
    for m in member_list:
        m.corpDate = print_date(m.corpDate)
        m.lastLogin = print_date(m.lastLogin)
        m.lastLogoff = print_date(m.lastLogoff)
        m.location = resolveLocationName(m.locationID)
    return member_list
    
    
def getScanDate():
    date = UpdateDate.objects.get(model_name=Member.__name__) 
    return date.update_date
