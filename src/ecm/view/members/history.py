'''
This file is part of ESM

Created on 13 mars 2011
@author: diabeteman
'''
from esm.core import utils
from esm import settings
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from esm.view import getScanDate
from esm.data.roles.models import Member, MemberDiff
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
import json
from django.utils.text import truncate_words
from esm.core.utils import print_time_min




#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def history(request):
    data = {
        'scan_date' : getScanDate(Member.__name__) 
    }
    return render_to_response("members/member_history.html", data, context_instance=RequestContext(request))


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
