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
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils.translation import ugettext as tr

from ecm import apps, plugins
from ecm.utils.c_s_v import CSVUnicodeWriter
from ecm.utils import _json as json
from ecm.apps.common.models import UrlPermission, Setting
from ecm.apps.common.auth import get_directors_group
from ecm.apps.scheduler.models import ScheduledTask
from ecm.apps.corp.models import SharedData

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
    'sDom': '<"row-fluid"<"span5"l><"span7"p>>rt<"row-fluid"<"span5"i><"span7"p>>',
    'fnStateLoadParams': 'function (oSettings, oData) { oData.sFilter = $("#search_text").val(); }',
    'fnStateSaveParams': 'function (oSettings, oData) { $("#search_text").val(oData.sFilter); return true; }',
    'oLanguage': {
        'sLengthMenu': tr('_MENU_ lines per page'),
        'sZeroRecords': tr('Nothing found to display - sorry.'),
        'sInfo': tr('Showing _START_ to _END_ of _TOTAL_ records'),
        'sInfoEmpty': tr('Showing 0 to 0 of 0 records'),
        'sInfoFiltered': tr('(filtered from _MAX_ total records)'),
    },
    'oSaveAsCSV': {
        'sButtonText': tr('Save as CSV'),
        'sButtonClass': 'btn pull-right',
        'sIconClass': 'icon-download-alt',
    },
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
    params.format = REQ.get("sFormat")
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
def datatable_csv_data(data, headers=None, filename=None):
    
    csv_writer = CSVUnicodeWriter(stream=StringIO())
    
    if headers is not None:
        csv_writer.writerow(headers)
    csv_writer.writerows(data)
    
    response = HttpResponse(csv_writer.stream.getvalue(), mimetype='text/csv')
    if filename is not None:
        response['Content-Disposition'] = 'attachment;filename="%s"' % filename
        
    return response

#------------------------------------------------------------------------------
def create_app_objects(app):
    for task in app.tasks:
        if not ScheduledTask.objects.filter(function=task['function']):
            # we only consider the function as these tasks should
            # be unique in the database
            ScheduledTask.objects.create(**task)
            logger.info("Created task '%s'" % task['function'])
    for name, value in app.settings.items():
        if not Setting.objects.filter(name=name):
            Setting.objects.create(name=name, value=repr(value))
            logger.info("Created Setting %s=%s" % (repr(name), repr(value)))
    for perm in app.permissions:
        if not UrlPermission.objects.filter(pattern=perm):
            try:
                directors = get_directors_group()
                newPattern = UrlPermission.objects.create(pattern=perm)
                newPattern.groups.add(directors)
                logger.info("Created UrlPermission r'%s'" % perm)
            except:
                # The init order is such that with a fresh DB the director's group is unknown until the HR settings are loaded, which is later in the app list
                # Ignore and this will get hit later, hopefully.
                pass
    for share in app.shared_data:
        url = share['url']
        if not url.startswith('/'):
            url = '/%s/' % app.app_prefix + url
        handler = share['handler']
        if not SharedData.objects.filter(url=url):
            SharedData.objects.create(url=url, handler=handler)
            logger.info("Created SharedData %r" % url)
        else:
            SharedData.objects.filter(url=url).update(handler=handler)

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
def import_monkey_patches():
    import ecm.lib.templatepatch #@UnusedImport for multi line template tags
    from . import template_filters #@UnusedImport to register template tags/filters
import_monkey_patches()
