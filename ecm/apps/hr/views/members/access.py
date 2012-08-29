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

from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response
from django.http import HttpResponseBadRequest
from django.template.context import RequestContext as Ctx
from django.utils.translation import ugettext as tr

from ecm.apps.common.models import UpdateDate, ColorThreshold
from ecm.utils.format import print_time_min
from ecm.views import extract_datatable_params, datatable_ajax_data, DATATABLES_DEFAULTS
from ecm.apps.hr.models import TitleMembership, RoleMemberDiff, TitleMemberDiff, Member
from ecm.views.decorators import check_user_access

ACCESS_CHANGES_COLUMNS = [
    {'sTitle': tr('Change'),         'sWidth': '5%',    'stype': 'string', },
    {'sTitle': tr('Member'),         'sWidth': '15%',   'stype': 'string', },
    {'sTitle': tr('Title/Role'),     'sWidth': '50%',   'stype': 'html', },
    {'sTitle': tr('Date'),           'sWidth': '25%',   'stype': 'string', },
]

#------------------------------------------------------------------------------
@check_user_access()
def access_changes(request):
    data = {
        'scan_date' : UpdateDate.get_latest(TitleMembership),
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl': Member.DIRECTOR_ACCESS_LVL,
        'datatable_defaults': DATATABLES_DEFAULTS,
        'columns' : ACCESS_CHANGES_COLUMNS,
        'sorting': [[3, 'desc']],
        'ajax_url': '/hr/members/accesschanges/data/',
    }

    return render_to_response("ecm/hr/members/access_changes.html", data, Ctx(request))

#-----------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def access_changes_data(request):
    try:
        params = extract_datatable_params(request)
        if params.column == 1:
            lambda_sort = lambda e: e.member.name.lower()
        else:
            lambda_sort = lambda e: e.date
    except:
        return HttpResponseBadRequest()

    roles_query = RoleMemberDiff.objects.select_related(depth=1).all()
    titles_query = TitleMemberDiff.objects.select_related(depth=1).all()

    if params.search:
        total_count = roles_query.count() + titles_query.count()
        roles_search_args = Q(member__name__icontains=params.search) | Q(role__roleName__icontains=params.search)
        roles_query = roles_query.filter(roles_search_args)
        titles_search_args = Q(member__name__icontains=params.search) | Q(title__titleName__icontains=params.search)
        titles_query = titles_query.filter(titles_search_args)
        filtered_count = roles_query.count() + titles_query.count()
    else:
        total_count = filtered_count = roles_query.count() + titles_query.count()

    changes = list(roles_query) + list(titles_query)
    changes.sort(key=lambda_sort, reverse=not params.asc)
    changes = changes[params.first_id:params.last_id]

    change_list = []
    for c in changes:
        change_list.append([
            c.new,
            c.member_permalink,
            c.access_permalink,
            print_time_min(c.date)
        ])

    return datatable_ajax_data(change_list, params.sEcho, total_count, filtered_count)
