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

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page
from django.http import HttpResponseBadRequest
from django.template.context import RequestContext as Ctx

from ecm.utils import db
from ecm.utils.format import print_time_min
from ecm.apps.hr.models import TitleComposition, Title, TitleCompoDiff
from ecm.apps.common.models import ColorThreshold, UpdateDate
from ecm.apps.hr.views import TITLES_COLUMNS
from ecm.views.decorators import check_user_access
from ecm.views import datatable_ajax_data, extract_datatable_params, DATATABLES_DEFAULTS
from ecm.apps.hr import NAME as app_prefix

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
all_columns = [ "titleName", "accessLvl" ]
@check_user_access()
@cache_page(3 * 60 * 60) # 3 hours cache
def titles_data(request):
    try:
        params = extract_datatable_params(request)
    except KeyError:
        return HttpResponseBadRequest()

    titles = getTitles(sort_by=all_columns[params.column], asc=params.asc)

    return datatable_ajax_data(titles, params.sEcho)

#------------------------------------------------------------------------------
SQL_TITLE_MEMBERS = '''SELECT COUNT(*)
FROM "hr_titlemembership"
WHERE "hr_titlemembership"."title_id"="hr_title"."titleID"'''
SQL_ROLES_IN_TITLES = '''SELECT COUNT(*)
FROM "hr_titlecomposition"
WHERE "hr_titlecomposition"."title_id"="hr_title"."titleID"'''
SQL_TITLE_MEMBERS = db.fix_mysql_quotes(SQL_TITLE_MEMBERS)
SQL_ROLES_IN_TITLES = db.fix_mysql_quotes(SQL_ROLES_IN_TITLES)

def getTitles(sort_by="titleID", asc=True):
    sort_col = "%s_nocase" % sort_by

    query = Title.objects.all().order_by("titleID")

    # SQL hack for making a case insensitive sort
    query = query.extra(select={sort_col : 'LOWER("%s")' % sort_by})
    if not asc: sort_col = "-" + sort_col
    query = query.extra(order_by=[sort_col])

    # fetch the number of members having each title
    query = query.extra(select={
        "title_members" : SQL_TITLE_MEMBERS,
        "roles_in_title": SQL_ROLES_IN_TITLES
    })

    titles = []
    for title in query:
        modification_date = TitleCompoDiff.objects.filter(title=title).order_by("-id")
        if modification_date.count():
            modification_date = print_time_min(modification_date[0].date)
        else:
            modification_date = "-"

        titles.append([
            title.permalink,
            title.accessLvl,
            '<a href="/%s/titles/%d/members/">%d</a>' % (app_prefix, title.titleID, title.title_members),
            title.roles_in_title,
            modification_date
        ])

    return titles
