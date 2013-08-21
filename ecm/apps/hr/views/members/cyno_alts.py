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

__date__ = "2013 8 14"
__author__ = "ajurna"

import logging

from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.db.models.aggregates import Count
from django.template.context import RequestContext as Ctx
from django.utils.translation import ugettext as tr


from ecm.apps.corp.models import Corporation
from ecm.views import DATATABLES_DEFAULTS, datatable_csv_data
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.apps.hr.models import Member
from ecm.apps.common.models import UpdateDate
from ecm.utils import db, _json as json
from ecm.apps.corp.models import Standing
from ecm.apps.common.models import UrlPermission

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
MEMBERS_COLUMNS = [
    {'sTitle': tr('Name'),         'sWidth': '15%',   'db_field': 'name', },
    {'sTitle': tr('Corp'),         'sWidth': '5%',    'db_field': 'corp__corporationName', },
    {'sTitle': tr('Standing'),     'sWidth': '5%',     },
    {'sTitle': tr('Player'),       'sWidth': '15%',   'db_field': 'owner__username', },
    {'sTitle': tr('Location'),     'sWidth': '20%',   'db_field': 'location', },
]
#------------------------------------------------------------------------------
@check_user_access()
def cyno_list(request):
    corps = Corporation.objects.others().order_by('corporationName')
    corps = corps.annotate(member_count=Count('members'))

    data = {
        'scan_date' : UpdateDate.get_latest(Member),
        'trusted_corps': corps.filter(member_count__gt=0, is_trusted=True),
        'other_corps': corps.filter(member_count__gt=0, is_trusted=False),
        'datatables_defaults': DATATABLES_DEFAULTS,
        'columns': MEMBERS_COLUMNS,
        'ajax_url': '/hr/cyno_alts/data/',
    }
    return render_to_response("ecm/hr/members/cyno_alts.html", data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def cyno_alts_data(request):
    try:
        params = extract_datatable_params(request)
        corp_id = request.GET.get('corp')
    except KeyError:
        return HttpResponseBadRequest()

    if corp_id:
        try:
            query = Corporation.objects.get(corporationID=int(corp_id)).members.filter(is_cyno_alt=True)
        except Corporation.DoesNotExist:
            query = Corporation.objects.mine().members.filter(is_cyno_alt=True)
        except ValueError:
            # corp_id cannot be casted to int, we take all corps
            query = Member.objects.exclude(corp=None).filter(is_cyno_alt=True)
    else:
        query = Corporation.objects.mine().members.all()

    total_members,\
    filtered_members,\
    members = get_members(query=query,
                          first_id=params.first_id,
                          last_id=params.last_id,
                          search_str=params.search,
                          sort_by=params.column,
                          asc=params.asc,
                          for_csv=params.format == 'csv')

    if params.format == 'csv':
        return datatable_csv_data(members, filename='members.csv')
    else:
        return datatable_ajax_data(members, params.sEcho, total_members, filtered_members)

#------------------------------------------------------------------------------
def get_members(query, first_id, last_id, search_str=None, sort_by=0, asc=True, for_csv=False):

    query = query.select_related(depth=2) # improve performance

    sort_col = MEMBERS_COLUMNS[sort_by]['db_field']
    # SQL hack for making a case insensitive sort
    if sort_by == 0:
        sort_col = sort_col + "_nocase"
        sort_val = db.fix_mysql_quotes('LOWER("%s")' % MEMBERS_COLUMNS[sort_by]['db_field'])
        query = query.extra(select={ sort_col : sort_val })


    if not asc: sort_col = "-" + sort_col
    query = query.extra(order_by=([sort_col]))

    if search_str:
        total_members = query.count()
        search_args = Q(name__icontains=search_str) | Q(nickname__icontains=search_str)

        if "DIRECTOR".startswith(search_str.upper()):
            search_args = search_args | Q(accessLvl=Member.DIRECTOR_ACCESS_LVL)

        query = query.filter(search_args)
        filtered_members = query.count()
    else:
        total_members = filtered_members = query.count()
    
    my_corp = Corporation.objects.mine()
    member_list = []
    if for_csv:
        for member in query:
            member_list.append([
                member.name,
                member.corp or '-',
                get_standing(member, my_corp),
                member.owner or '-',
                member.location,
            ])
    else:
        for member in query[first_id:last_id]:

            if member.corp:
                corp = '<span title="%s">%s</span>' % (member.corp, member.corp.ticker)
            else:
                corp = '-'

            memb = [
                member.permalink,
                corp,
                get_standing(member, my_corp),
                member.owner_permalink,
                member.dotlan_location,
            ]

            member_list.append(memb)

    return total_members, filtered_members, member_list

#------------------------------------------------------------------------------
def get_standing(member, my_corp):

    if member.corp == my_corp:
        return 'Corp'
    elif member.corp.alliance == my_corp.alliance:
        return 'Alliance'

    # first look at corp standings (they have priority over alliance)
    corp_standings = my_corp.standings.filter(is_corp_contact=True)
    try:
        return corp_standings.get(contactID=member.characterID).value
    except Standing.DoesNotExist:
        pass
    try:
        return corp_standings.get(contactID=member.corp_id).value
    except Standing.DoesNotExist:
        pass
    if member.corp.alliance_id:
        try:
            return corp_standings.get(contactID=member.corp.alliance_id).value
        except Standing.DoesNotExist:
            pass

    # then look at alliance standings
    alliance_standings = my_corp.standings.filter(is_corp_contact=False)
    try:
        return alliance_standings.get(contactID=member.characterID).value
    except Standing.DoesNotExist:
        pass
    try:
        return alliance_standings.get(contactID=member.corp_id).value
    except Standing.DoesNotExist:
        pass
    if member.corp.alliance_id:
        try:
            return alliance_standings.get(contactID=member.corp.alliance_id).value
        except Standing.DoesNotExist:
            pass

    # no standing towards this member
    return 'Neutral'

#------------------------------------------------------------------------------
@login_required
def is_cyno_alt(request, characterID):
    """
    Serves /hr/members/<characterID>/is_cyno_alt/
    """
    member = get_object_or_404(Member, characterID=int(characterID))
    if not (request.user.is_superuser or
        request.user == member.owner or
        UrlPermission.user_has_access(request.user, request.get_full_path())):
        return HttpResponseForbidden(request)
    if request.method == 'POST':
        try:
            is_cyno_alt = bool(json.loads(request.POST.get('is_cyno_alt')))
        except (ValueError, TypeError), e:
            return HttpResponseBadRequest(str(e))
        member.is_cyno_alt = is_cyno_alt
        member.save()
        logger.info('"%s" Changed cyno alt status of "%s" -> %s' % (request.user, member, is_cyno_alt))

    return HttpResponse(json.dumps(member.is_cyno_alt))
