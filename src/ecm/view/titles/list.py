'''
This file is part of EVE Corporation Management

Created on 11 juil. 2010
@author: diabeteman
'''

import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse

from ecm.data.roles.models import TitleComposition, Title, TitleCompoDiff
from ecm.data.common.models import ColorThreshold
from ecm.core import utils
from ecm import settings
from ecm.view import getScanDate

#------------------------------------------------------------------------------
@user_passes_test(lambda user: utils.isDirector(user), login_url=settings.LOGIN_URL)
@cache_page(3 * 60 * 60 * 15) # 3 hours cache
@csrf_protect
def all(request):
    colorThresholds = []
    for c in ColorThreshold.objects.all().order_by("threshold"):
        colorThresholds.append({ "threshold" : c.threshold, "color" : c.color })

    data = { 
        'scan_date' : getScanDate(TitleComposition.__name__), 
        'colorThresholds' : json.dumps(colorThresholds)
    }
    return render_to_response("titles/titles.html", data, context_instance=RequestContext(request))

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
    titlesDb = titlesDb.extra(select={"title_members" : "SELECT COUNT(*) "
                                      "FROM roles_titlemembership, roles_member "
                                      "WHERE roles_titlemembership.title_id = roles_title.titleID "
                                      "AND roles_titlemembership.member_id = roles_member.characterID "
                                      "AND roles_member.corped = 1"})

    titles = []
    for t in titlesDb:
        modification_date = TitleCompoDiff.objects.filter(title=t).order_by("-id")
        if modification_date.count():
            modification_date = utils.print_time_min(modification_date[0].date)
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
