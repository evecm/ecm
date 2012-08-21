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

__date__ = "2010-05-16"
__author__ = "diabeteman"

from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.context import RequestContext as Ctx


from ecm.views import DATATABLES_DEFAULTS
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.apps.hr.models import Member
from ecm.apps.common.models import ColorThreshold, UpdateDate
from ecm.apps.hr.views import get_members, MEMBERS_COLUMNS

#------------------------------------------------------------------------------
@check_user_access()
def members(request):
    data = {
        'scan_date' : UpdateDate.get_latest(Member),
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL,
        'datatables_defaults': DATATABLES_DEFAULTS,
        'columns': MEMBERS_COLUMNS,
        'ajax_url': '/hr/members/data/',
    }
    return render_to_response("ecm/hr/members/member_list.html", data, Ctx(request))

#------------------------------------------------------------------------------
SUPER_CAPITALS = [
    'Erebus', # <3
    'Avatar', 
    'Leviathan', # ugly
    'Ragnarok',
    'Nyx', # <3
    'Aeon', # space taco
    'Wyvern', # ugliest
    'Hel', 
]
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def members_data(request):
    try:
        params = extract_datatable_params(request)
        ships = request.GET.get('show_ships', 'all')
    except KeyError:
        return HttpResponseBadRequest()
    
    query = Member.objects.filter(corped=True)
    if ships == 'supers':
        query = query.filter(ship__in=SUPER_CAPITALS)
    
    total_members,\
    filtered_members,\
    members = get_members(query=query,
                          first_id=params.first_id,
                          last_id=params.last_id,
                          search_str=params.search,
                          sort_by=params.column,
                          asc=params.asc)

    return datatable_ajax_data(members, params.sEcho, total_members, filtered_members)

#------------------------------------------------------------------------------
@check_user_access()
def unassociated(request):
    data = {
        'scan_date' : UpdateDate.get_latest(Member),
        'colorThresholds' : ColorThreshold.as_json(),
        'directorAccessLvl' : Member.DIRECTOR_ACCESS_LVL,
        'datatables_defaults': DATATABLES_DEFAULTS,
        'columns': MEMBERS_COLUMNS,
        'ajax_url': '/hr/members/unassociated/data/',
    }
    return render_to_response("ecm/hr/members/unassociated.html", data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def unassociated_data(request):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    total_members,\
    filtered_members,\
    members = get_members(query=Member.objects.filter(corped=True, owner=None),
                          first_id=params.first_id,
                          last_id=params.last_id,
                          search_str=params.search,
                          sort_by=params.column,
                          asc=params.asc)

    return datatable_ajax_data(members, params.sEcho, total_members, filtered_members)

#------------------------------------------------------------------------------
@check_user_access()
@cache_page(60 * 60) # 1 hour cache
def unassociated_clip(request):
    query = Member.objects.filter(corped=True, owner=None).order_by("name")
    data = query.values_list("name", flat=True)
    return HttpResponse("\n".join(data))
#------------------------------------------------------------------------------
import csv
@check_user_access()
def export_to_csv(request):
    # Get response object, this can be used as a stream.
    response = HttpResponse(mimetype="text/csv")
    # Force download
    response['Content-Disposition'] = 'attachment;filename="member_export.csv"' 

    # csv writer
    writer = csv.writer(response)
    writer.writerow(['Name','Nickname', 'Player', 'Access Level', 'Last Login', 'Location', 'Ship'])
    for member in Member.objects.all():
        writer.writerow([member.name, 
                member.nickname, 
                member.owner,
                member.accessLvl, 
                str(member.lastLogin).split('+')[0], 
                member.location, 
                member.ship,
                ]) 



    return response
    
   
