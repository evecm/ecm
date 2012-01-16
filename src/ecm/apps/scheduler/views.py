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

__date__ = "2011 10 26"
__author__ = "diabeteman"

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json
import time
import httplib as http
from datetime import datetime
import logging

from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from ecm import apps, plugins
from ecm.views import extract_datatable_params
from ecm.views.decorators import basic_auth_required, check_user_access
from ecm.apps.scheduler.models import ScheduledTask
from ecm.apps.scheduler.threads import TaskThread


LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@basic_auth_required(username=settings.CRON_USERNAME)
def trigger_scheduler(request):
    now = datetime.now()
    tasks_to_execute = ScheduledTask.objects.filter(is_active=True,
                                                    is_running=False,
                                                    next_execution__lt=now).order_by("-priority")
    if tasks_to_execute:
        TaskThread(tasks=tasks_to_execute).start()
        return HttpResponse(status=http.ACCEPTED)
    else:
        return HttpResponse(status=http.NOT_MODIFIED)

#------------------------------------------------------------------------------
@check_user_access()
def task_list(request):
    return render_to_response('tasks.html', RequestContext(request))

#------------------------------------------------------------------------------
FUNCTIONS = []
for app in apps.LIST:
    FUNCTIONS += [ t['function'] for t in app.tasks ]
for plugin in plugins.LIST:
    FUNCTIONS += [ t['function'] for t in plugin.tasks ]
FUNCTIONS.sort()

@check_user_access()
def task_list_data(request):
    try:
        params = extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()

    tasks = []
    query = ScheduledTask.objects.filter(function__in=FUNCTIONS, is_active=True)
    for t in query.order_by('function'):
        tasks.append([
            t.function,
            t.next_execution_admin_display(),
            t.frequency_admin_display(),
            t.is_running,
            t.as_html(nexturl='/scheduler/tasks/')
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : len(tasks),
        "iTotalDisplayRecords" : len(tasks),
        "aaData" : tasks
    }

    return HttpResponse(json.dumps(json_data))


#------------------------------------------------------------------------------
@check_user_access()
def launch_task(request, task_id):
    try:
        task = ScheduledTask.objects.get(id=int(task_id))
    except ScheduledTask.DoesNotExist:
        return HttpResponseNotFound('No task with ID ' + task_id)
    except ValueError, e:
        raise HttpResponseBadRequest(str(e))

    if task.is_running:
        code = http.NOT_MODIFIED
        LOG.warning("Task '%s' is already running." % task.function)
    elif not task.is_active:
        code = http.NOT_MODIFIED
        LOG.warning("Task '%s' is disabled." % task.function)
    else:
        code = http.ACCEPTED
        TaskThread(tasks=[task]).start()

    next_page = request.GET.get("next", None)
    if next_page is not None:
        # we let the task the time to start before redirecting
        # so the "next" web page can display that it is actually running
        time.sleep(0.2)
        return redirect(next_page)
    else:
        return HttpResponse(status=code)

