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

__date__ = "2011 4 17"
__author__ = "diabeteman"

from django.http import HttpResponseBadRequest, HttpResponse, Http404
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models.aggregates import Count
from django.template.context import RequestContext as Ctx
from django.utils.translation import ugettext as tr

from ecm.utils import _json as json
from ecm.views.decorators import check_user_access
from ecm.utils.format import print_time_min
from ecm.apps.hr.models import Member, Recruit
from ecm.apps.common.models import ColorThreshold
from ecm.views import extract_datatable_params, datatable_ajax_data, DATATABLES_DEFAULTS
from ecm.apps.hr.views import get_members, MEMBERS_COLUMNS

PLAYERS_COLUMNS = [
    {'sTitle': tr('Username'),     'sWidth': '30%',   'db_field': 'username', },
    {'sTitle': tr('Admin'),        'sWidth': '10%',   'db_field': 'is_superuser', },
    {'sTitle': tr('EVE Accounts'), 'sWidth': '10%',   'db_field': 'account_count', },
    {'sTitle': tr('Characters'),   'sWidth': '10%',   'db_field': 'char_count', },
    {'sTitle': tr('Groups'),       'sWidth': '10%',   'db_field': 'group_count', },
    {'sTitle': tr('Last Login'),   'sWidth': '15%',   'db_field': 'last_login', },
    {'sTitle': tr('Joined Date'),  'sWidth': '15%',   'db_field': 'date_joined', },
]
#------------------------------------------------------------------------------
@check_user_access()
def player_list(request):
    data = {
        'colorThresholds'     : ColorThreshold.as_json(),
        'player_columns'      : PLAYERS_COLUMNS,
        'datatables_defaults' : DATATABLES_DEFAULTS,
    }
    return render_to_response("ecm/hr/players/player_list.html", data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def player_list_data(request):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    query = User.objects.select_related(depth=2).filter(is_active=True)
    query = query.annotate(account_count=Count("eve_accounts"))
    query = query.annotate(char_count=Count("characters"))
    query = query.annotate(group_count=Count("groups"))
    query = query.filter(eve_accounts__gt=0)

    sort_by = PLAYERS_COLUMNS[params.column]['db_field']
    # SQL hack for making a case insensitive sort
    if sort_by == "username":
        sort_col = "%s_nocase" % sort_by
        query = query.extra(select={sort_col : 'LOWER("%s")' % sort_by})
    else:
        sort_col = sort_by

    if not params.asc: sort_col = "-" + sort_col
    query = query.extra(order_by=[sort_col])

    if params.search:
        total_count = query.count()
        query = query.filter(username__icontains=params.search)
        filtered_count = query.count()
    else:
        total_count = filtered_count = query.count()

    player_list = []
    for player in query[params.first_id:params.last_id]:
        player_list.append([
            '<a href="/hr/players/%d/" class="player">%s</a>' % (player.id, player.username),
            player.is_staff and player.is_superuser,
            player.eve_accounts.all().count(),
            player.characters.all().count(),
            player.groups.all().count(),
            print_time_min(player.last_login),
            print_time_min(player.date_joined)
        ])

    return datatable_ajax_data(player_list, params.sEcho, total_count, filtered_count)

#------------------------------------------------------------------------------
@check_user_access()
def player_details(request, player_id):
    player = get_object_or_404(User, id=int(player_id))

    try:
        player = User.objects.select_related(depth=1).get(id=int(player_id))
    except User.DoesNotExist:
        raise Http404()

    eve_accounts = player.eve_accounts.all().count()
    characters = player.characters.all().count()
    
    groups = player.groups.all().order_by('id')

    reference = ''
    try:
        player.user
        counter = 1
        count = player.user.reference.all().all().count()
        if count > 0:
            for r in player.user.reference.all().all():
                url = '/hr/players/%d/' % r.id
                reference += '<a href="%s" class="player">%s</a>' % (url, r.username)
                if counter < count:
                    reference += ', '
                counter += 1
        else:
            reference = '-'
    except Recruit.DoesNotExist:
        reference = '-'
    
    try:
        if player.user.recruiter and player.user.recruiter.characters.all().count() > 0:
            recruiter = player.user.recruiter.characters.all()[0].owner_permalink
        else:
            recruiter = '-'
    except Recruit.DoesNotExist:
        recruiter = '-'

    data = {
        'player': player,
        'eve_accounts'        : eve_accounts,
        'characters'          : characters,
        'groups'              : groups,
        'reference'           : reference,
        'recruiter'           : recruiter,
        'colorThresholds'     : ColorThreshold.as_json(),
        'directorAccessLvl'   : Member.DIRECTOR_ACCESS_LVL,
        'player_columns'      : MEMBERS_COLUMNS,
        'datatables_defaults' : DATATABLES_DEFAULTS,
    }

    return render_to_response('ecm/hr/players/player_details.html', data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def player_details_data(request, player_id):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    player = get_object_or_404(User, id=int(player_id))

    total_members,\
    filtered_members,\
    members = get_members(query=Member.objects.filter(owner=player),
                          first_id=params.first_id,
                          last_id=params.last_id,
                          search_str=params.search,
                          sort_by=params.column,
                          asc=params.asc)
    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_members,
        "iTotalDisplayRecords" : filtered_members,
        "aaData" : members
    }

    return HttpResponse(json.dumps(json_data))

