'''
This file is part of ESM

Created on 13 mars 2011
@author: diabeteman
'''

from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from esm.view import getScanDate
from esm.data.roles.models import TitleMembership, RoleMemberDiff, TitleMemberDiff, TitleComposition,\
    TitleCompoDiff
from django.shortcuts import render_to_response
from esm.core import utils
from esm import settings
from django.template.context import RequestContext
import json
from django.http import HttpResponse, HttpResponseBadRequest
from esm.core.utils import print_time_min



#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def changes(request):
    data = {
        'scan_date' : getScanDate(TitleComposition.__name__) 
    }
    return render_to_response("titles/changes.html", data, context_instance=RequestContext(request))

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(60 * 60 * 15) # 1 hour cache
@csrf_protect
def changes_data(request):
    try:
        iDisplayStart = int(request.GET["iDisplayStart"])
        iDisplayLength = int(request.GET["iDisplayLength"])
        sEcho = int(request.GET["sEcho"])
    except:
        return HttpResponseBadRequest()

    count, changes = getTitleChanges(first_id=iDisplayStart, 
                                     last_id=iDisplayStart + iDisplayLength - 1)
    json_data = {
        "sEcho" : sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : changes
    }
    
    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
def getTitleChanges(first_id, last_id):
    
    titles = TitleCompoDiff.objects.all().order_by("-date")
    
    count = titles.count()
    
    changes = titles[first_id:last_id]
    
    change_list = []
    for c in changes:
        change = [
            c.new,
            '<a href="/titles/%d" class="title">%s</a>' % (c.title_id, unicode(c.title)),
            '<a href="/roles/%d/%d" class="role">%s</a>' % (c.role.roleType.id, c.role_id, unicode(c.role)),
            print_time_min(c.date)
        ]

        change_list.append(change)
    
    return count, change_list