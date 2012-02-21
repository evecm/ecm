# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.
from ecm.apps.hr.models.member import MemberSession
from datetime import timedelta
from django.utils.datetime_safe import datetime
from django.db.models.aggregates import Avg, Sum

__date__ = "2011-03-13"
__author__ = "diabeteman"


try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.template.context import RequestContext as Ctx

from ecm.apps.hr.models import MemberDiff, Member, RoleMemberDiff, TitleMemberDiff
from ecm.views import getScanDate, extract_datatable_params
from ecm.views.decorators import check_user_access
from ecm.apps.common.models import ColorThreshold, Setting
from ecm.core.utils import print_time_min, get_access_color
from ecm.core.eve import db

import logging
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@check_user_access()
def details(request, characterID):
    avg_session = {}
    avg_session['sessionlength'] = 0
    avg_session['30days'] = 0
    avg_session['7days'] = 0
    try:
        colorThresholds = ColorThreshold.objects.all().order_by("threshold")
        member = Member.objects.get(characterID=int(characterID))
        member.base = db.resolveLocationName(member.baseID)[0]
        member.color = get_access_color(member.accessLvl, colorThresholds)
        member.roles_no_director = member.roles.exclude(roleID=1) # exclude 'director'
        avg_session['sessionlength'] = timedelta(seconds=
                MemberSession.objects.filter(character_id = member.characterID,
                                             session_begin__gt = (datetime.now() - timedelta(30))
                                            )
                                    .aggregate(sessionlength=Avg('session_seconds'))['sessionlength'])
        avg_session['30days'] = timedelta(seconds=
                MemberSession.objects.filter(character_id = member.characterID,
                                             session_begin__gt = (datetime.now() - timedelta(30))
                                            )
                                          .aggregate(length=Sum('session_seconds'))['length'])
        avg_session['7days'] = timedelta(seconds=
                MemberSession.objects.filter(character_id = member.characterID,
                                             session_begin__gt = (datetime.now() - timedelta(7))
                                            )
                                          .aggregate(length=Sum('session_seconds'))['length'])
        loginhistory = MemberSession.objects.filter(character_id=member.characterID).order_by('-session_begin')[:10]
        if member.corped:
            member.date = getScanDate(Member)
        else:
            d = MemberDiff.objects.filter(member=member, new=False).order_by("-id")[0]
            member.date = d.date
    except ObjectDoesNotExist:
        member = Member(characterID=int(characterID), name="???")

    try:
        killboardUrl = Setting.get('corp_killboard_url')
    except Setting.DoesNotExist:
        killboardUrl = None

    data = { 'member' : member, 'killboardUrl': killboardUrl,
            'sessiondata': avg_session, 'logins': loginhistory}
    return render_to_response("members/member_details.html", data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def update_member_notes(request, characterID):
    try:
        new_notes = request.POST["value"]
        member = get_object_or_404(Member, characterID=int(characterID))
        member.notes = new_notes
        member.save()

        logger.info('"%s" edited notes on "%s" : %s' % (request.user, member, new_notes))

        return HttpResponse(new_notes)
    except:
        return HttpResponseBadRequest()


#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def access_changes_member_data(request, characterID):
    try:
        params = extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()

    roles = RoleMemberDiff.objects.filter(member=characterID).order_by("-id")
    titles = TitleMemberDiff.objects.filter(member=characterID).order_by("-id")

    count = roles.count() + titles.count()

    changes = list(roles) + list(titles)
    changes.sort(key=lambda e: e.date, reverse=True)
    changes = changes[params.first_id:params.last_id]

    change_list = []
    for change in changes:
        change_list.append([
            change.new,
            change.access_permalink,
            print_time_min(change.date)
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : count,
        "iTotalDisplayRecords" : count,
        "aaData" : change_list
    }

    return HttpResponse(json.dumps(json_data))
