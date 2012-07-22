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

__date__ = "2010-02-03"
__author__ = "diabeteman"

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.http import HttpResponse
from django.db.models import Q
from django.utils.text import truncate_words
from django.contrib.auth.models import User
from django.utils.translation import ugettext as tr

from ecm import apps, plugins
from ecm.apps.hr.models import Member
from ecm.apps.common.models import UpdateDate, UrlPermission, Setting
from ecm.apps.scheduler.models import ScheduledTask
from ecm.views import template_filters
from ecm.lib import templatepatch

import csv
import logging
logger = logging.getLogger(__name__)


JSON = 'text/json'
XML = 'text/xml'
HTML = 'text/html'

DATE_PATTERN = "%Y-%m-%d_%H-%M-%S"

#------------------------------------------------------------------------------
DATATABLES_DEFAULTS = {
    'sPaginationType': 'bootstrap',
    'bProcessing': True,
    'bServerSide': True,
    'bAutoWidth': False,
    'iDisplayLength': 25,
    'bStateSave': True,
    'iCookieDuration': 60 * 60, # 1 hour
    'sDom': "<'row-fluid'<'span5'l><'span7'p>T>rt<'row-fluid'<'span5'i><'span7'p>>",
    'oTableTools': {
        'sSwfPath': "/static/ecm/swf/copy_csv_xls.swf",
        'aButtons': ["copy", "csv" ],
        },
    'fnStateLoadParams': 'function (oSettings, oData) { oData.sFilter = $("#search_text").val(); }',
    'fnStateSaveParams': 'function (oSettings, oData) { $("#search_text").val(oData.sFilter); return true; }',
    'oLanguage': {
        'sLengthMenu': tr('_MENU_ lines per page'),
        'sZeroRecords': tr('Nothing found to display - sorry.'),
        'sInfo': tr('Showing _START_ to _END_ of _TOTAL_ records'),
        'sInfoEmpty': tr('Showing 0 to 0 of 0 records'),
        'sInfoFiltered': tr('(filtered from _MAX_ total records)'),
    }
}

#------------------------------------------------------------------------------
class DatatableParams: pass
def extract_datatable_params(request):
    REQ = request.GET if request.method == 'GET' else request.POST
    params = DatatableParams()
    params.first_id = int(REQ["iDisplayStart"])
    params.length = int(REQ["iDisplayLength"])
    params.last_id = params.first_id + params.length
    params.search = REQ["sSearch"]
    params.sEcho = int(REQ["sEcho"])
    params.column = int(REQ["iSortCol_0"])
    params.asc = REQ["sSortDir_0"] == "asc"
    return params

#------------------------------------------------------------------------------
def datatable_ajax_data(data, echo, total=None, filtered=None):
    if total is None:
        total = len(data)
    if filtered is None:
        filtered = total
    json_data = {
        'sEcho' : echo,
        'iTotalRecords' : total,
        'iTotalDisplayRecords' : filtered,
        'aaData' : data,
    }
    return HttpResponse(json.dumps(json_data), mimetype=JSON)

#------------------------------------------------------------------------------
def create_app_objects(app):
    for task in app.tasks:
        if not ScheduledTask.objects.filter(function=task['function']):
            # we only consider the function as these tasks should
            # be unique in the database
            ScheduledTask.objects.create(**task)
            logger.info("Created task '%s'" % task['function'])
    for perm in app.permissions:
        if not UrlPermission.objects.filter(pattern=perm):
            UrlPermission.objects.create(pattern=perm)
            logger.info("Created UrlPermission r'%s'" % perm)
    for name, value in app.settings.items():
        if not Setting.objects.filter(name=name):
            Setting.objects.create(name=name, value=repr(value))
            logger.info("Created Setting %s=%s" % (repr(name), repr(value)))

# The creation of the declared objects is delayed here.
# If not, it would crash at first try of synchronizing the db
# as tables are not created yet.
for app in apps.LIST:
    create_app_objects(app)
for plugin in plugins.LIST:
    create_app_objects(plugin)

# When the server is shutdown while a scheduled task is running, it gets frozen
# and cannot be triggered anymore.
# The first time this module is imported, we reset all the scheduled tasks to
# is_running = False to avoid this problem.
ScheduledTask.objects.all().update(is_running=False, is_scheduled=False)

#------------------------------------------------------------------------------
admin_username = Setting.get('common_admin_username')
if not User.objects.filter(username=admin_username):
    try:
        logger.info('superuser "%s" does not exists. Creating...' % admin_username)
        User.objects.create_superuser(username=admin_username, email='', password='adminecm')
    except:
        logger.exception("")
        raise
#-----------------------------------------------------------------------------
