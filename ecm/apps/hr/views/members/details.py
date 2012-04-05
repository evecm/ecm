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

__date__ = "2011-03-13"
__author__ = "diabeteman"

from datetime import timedelta

from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.template.context import RequestContext as Ctx
from django.utils.datetime_safe import datetime
from django.db.models.aggregates import Avg

from ecm.apps.hr.models.member import MemberSession
from ecm.apps.hr.models import MemberDiff, Member, RoleMemberDiff, TitleMemberDiff
from ecm.views import getScanDate, extract_datatable_params, datatable_ajax_data
from ecm.views.decorators import check_user_access
from ecm.apps.common.models import ColorThreshold, Setting
from ecm.utils.format import print_time_min
from ecm.apps.eve.models import CelestialObject

import logging
logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@check_user_access()
def details(request, characterID):
    avg_session = {
      'sessionlength': 0,
      '30days': 0,
      '7days': 0,
    }
    now = datetime.now()
    try:
        member = Member.objects.get(characterID=int(characterID))
        try:
            member.base = CelestialObject.objects.get(itemID = member.baseID).itemName
        except CelestialObject.DoesNotExist:
            member.base = '???'

        member.color = ColorThreshold.get_access_color(member.accessLvl)
        member.roles_no_director = member.roles.exclude(roleID=1) # exclude 'director'

        query = MemberSession.objects.filter(character_id=member.characterID)
        query_30 = query.filter(session_begin__gt=now - timedelta(30))
        query_7 = query.filter(session_begin__gt=now - timedelta(7))

        session_len = query.aggregate(len=Avg('session_seconds'))['len'] or 0
        session_len_30 = query_30.aggregate(len=Avg('session_seconds'))['len'] or 0
        session_len_7 = query_7.aggregate(len=Avg('session_seconds'))['len'] or 0

        loginhistory = query.order_by('-session_begin')[:10]

        avg_session['sessionlength'] = timedelta(seconds=session_len)
        avg_session['30days'] = timedelta(seconds=session_len_30)
        avg_session['7days'] = timedelta(seconds=session_len_7)

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

    data = {
        'member': member,
        'killboardUrl': killboardUrl,
        'sessiondata': avg_session,
        'logins': loginhistory
    }
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

    return datatable_ajax_data(change_list, params.sEcho, count)
