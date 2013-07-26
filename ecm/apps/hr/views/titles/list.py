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

__date__ = "2010-07-11"
__author__ = "diabeteman"

from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.http import HttpResponseBadRequest
from django.template.context import RequestContext as Ctx
from django.utils.translation import ugettext as tr

from ecm.utils import db
from ecm.utils import _json as json
from ecm.utils.format import print_time_min
from ecm.apps.hr.models import TitleComposition, Title
from ecm.apps.common.models import ColorThreshold, UpdateDate
from ecm.apps.corp.models import Corporation
from ecm.views.decorators import check_user_access
from ecm.views import datatable_ajax_data, extract_datatable_params, DATATABLES_DEFAULTS
from ecm.apps.hr import NAME as app_prefix

TITLES_COLUMNS = [
    {'sTitle': tr('Title Name'),     'sWidth': '40%', 'db_field': 'titleName', },
    {'sTitle': tr('Access Level'),   'sWidth': '20%', 'db_field': 'accessLvl', },
    {'sTitle': tr('Members'),        'sWidth': '10%', 'db_field': None, 'bSortable': False, },
    {'sTitle': tr('Role Count'),     'sWidth': '10%', 'db_field': None, 'bSortable': False, },
    {'sTitle': tr('Last Modified'),  'sWidth': '20%', 'db_field': None, 'bSortable': False, },
]

#------------------------------------------------------------------------------
@check_user_access()
def titles(request):
    colorThresholds = []
    for c in ColorThreshold.objects.all().order_by("threshold"):
        colorThresholds.append({ "threshold" : c.threshold, "color" : c.color })

    data = {
        'scan_date' : UpdateDate.get_latest(TitleComposition),
        'colorThresholds' : json.dumps(colorThresholds),
        'columns': TITLES_COLUMNS,
        'datatables_defaults': DATATABLES_DEFAULTS
    }
    return render_to_response("ecm/hr/titles/titles.html", data, Ctx(request))

#------------------------------------------------------------------------------
SQL_TITLE_MEMBERS = db.fix_mysql_quotes('''SELECT COUNT(*)
FROM "hr_titlemembership"
WHERE "hr_titlemembership"."title_id"="hr_title"."id"''')
SQL_ROLES_IN_TITLES = db.fix_mysql_quotes('''SELECT COUNT(*)
FROM "hr_titlecomposition"
WHERE "hr_titlecomposition"."title_id"="hr_title"."id"''')

@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def titles_data(request):
    try:
        params = extract_datatable_params(request)
        corp_id = request.GET.get('corp')
    except KeyError:
        return HttpResponseBadRequest()

    if corp_id:
        try:
            query = Corporation.objects.get(corporationID=int(corp_id)).titles.all()
        except Corporation.DoesNotExist:
            query = Corporation.objects.mine().titles.all()
        except ValueError:
            # corp_id cannot be casted to int, we take all corps
            query = Title.objects.all()
    else:
        query = Corporation.objects.mine().titles.all()

    sort_by = TITLES_COLUMNS[params.column]['db_field']
    if params.column == 0:
        # SQL hack for making a case insensitive sort
        sort_col = "%s_nocase" % sort_by
        query = query.extra(select={sort_col: 'LOWER("%s")' % sort_by})
    else:
        sort_col = sort_by
    
    if not params.asc: 
        sort_col = "-" + sort_col
    query = query.extra(order_by=[sort_col])

    # fetch the number of members having each title
    query = query.extra(select={
        "title_members" : SQL_TITLE_MEMBERS,
        "roles_in_title": SQL_ROLES_IN_TITLES
    })
    
    titles = []
    for title in query:
        if title.title_compo_diffs.all():
            modification_date = print_time_min(title.title_compo_diffs.latest('id').date)
        else:
            modification_date = "-"

        titles.append([
            title.permalink,
            title.accessLvl,
            '<a href="/%s/titles/%d/members/">%d</a>' % (app_prefix, title.id, title.title_members),
            title.roles_in_title,
            modification_date
        ])

    return datatable_ajax_data(titles, params.sEcho)
