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

from django.views.decorators.cache import cache_page
from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext as Ctx
from django.utils.translation import ugettext as tr

from ecm.apps.common.models import ColorThreshold
from ecm.apps.hr.models import TitleCompoDiff, Title
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params, datatable_ajax_data, DATATABLES_DEFAULTS
from ecm.utils.format import print_time_min



#------------------------------------------------------------------------------
@check_user_access()
def details(request, title_id):

    title = get_object_or_404(Title, pk=int(title_id))
    
    if title.title_compo_diffs.all():
        title.lastModified = print_time_min(title.title_compo_diffs.latest('id'))
    else:
        title.lastModified = None
    
    title.color = ColorThreshold.get_access_color(title.accessLvl)

    data = {
        "title" : title,
        "member_count" : title.members.count(),
        "colorThresholds" : ColorThreshold.as_json(),
        'roles_columns': ROLES_COLUMNS,
        'diffs_columns': DIFFS_COLUMNS,
        'datatables_defaults': DATATABLES_DEFAULTS 
    }

    return render_to_response("ecm/hr/titles/title_details.html", data, Ctx(request))




#------------------------------------------------------------------------------
ROLES_COLUMNS = [
    {'sTitle': tr('Role'),           'sWidth': '50%',  'bSortable': False, },
    {'sTitle': tr('Category'),       'sWidth': '30%',  'bSortable': False, },
    {'sTitle': tr('Access Level'),   'sWidth': '20%',  'bSortable': False, },
]
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def composition_data(request, title_id):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    title = get_object_or_404(Title, pk=int(title_id))
    query = title.roles.all()

    if params.asc:
        query = query.order_by("roleID")
    else:
        query = query.order_by("-roleID")

    total_compos = query.count()

    query = query[params.first_id:params.last_id]

    role_list = []
    for role in query:
        role_list.append([
            role.permalink,
            role.roleType.permalink,
            role.get_access_lvl()
        ])

    return datatable_ajax_data(role_list, params.sEcho, total_compos)


#------------------------------------------------------------------------------
DIFFS_COLUMNS = [
    {'sTitle': tr('Change'),            'sWidth': '10%',  'bSortable': False, },
    {'sTitle': tr('Role'),              'sWidth': '40%',  'bSortable': False, },
    {'sTitle': tr('Category'),          'sWidth': '25%',  'bSortable': False, },
    {'sTitle': tr('Modification Date'), 'sWidth': '25%',  'bSortable': False, },
]
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def compo_diff_data(request, title_id):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    title = get_object_or_404(Title, pk=int(title_id))
    query = TitleCompoDiff.objects.filter(title=title).order_by("-date")
    total_diffs = query.count()

    query = query[params.first_id:params.last_id]

    diff_list = []
    for diff in query:
        diff_list.append([
            diff.new,
            diff.role.permalink,
            diff.role.roleType.permalink,
            print_time_min(diff.date)
        ])

    return datatable_ajax_data(diff_list, params.sEcho, total_diffs)
