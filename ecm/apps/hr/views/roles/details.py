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


from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.cache import cache_page
from django.http import HttpResponseBadRequest, Http404
from django.template.context import RequestContext as Ctx

from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params, datatable_ajax_data, DATATABLES_DEFAULTS
from ecm.apps.hr.models import Role, RoleType, Member
from ecm.apps.common.models import ColorThreshold
from ecm.apps.hr.views import get_members, MEMBERS_COLUMNS

#------------------------------------------------------------------------------
@check_user_access()
def role(request, role_id):
    try:
        role = get_object_or_404(Role, pk=int(role_id))
    except ValueError:
        raise Http404() 
    role.accessLvl = role.get_access_lvl()
    data = {
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL,
        'role_types' : RoleType.objects.all(),
        'role' : role,
        'ajax_url': '/hr/roles/%d/data/' % role.id,
        'direct_member_count' : role.members.count(),
        'total_member_count' : role.members_through_titles().count(),
        'columns': MEMBERS_COLUMNS,
        'datatables_defaults': DATATABLES_DEFAULTS,
    }
    return render_to_response("ecm/hr/roles/role_details.html", data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def role_data(request, role_id):
    try:
        params = extract_datatable_params(request)
        role = get_object_or_404(Role, pk=int(role_id))
    except (KeyError, ValueError), e:
        return HttpResponseBadRequest(str(e))

    total_members,\
    filtered_members,\
    members = get_members(query=role.members_through_titles(with_direct_roles=True),
                          first_id=params.first_id,
                          last_id=params.last_id,
                          search_str=params.search,
                          sort_by=params.column,
                          asc=params.asc)

    return datatable_ajax_data(members, params.sEcho, total_members, filtered_members)
