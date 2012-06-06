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

import time
import httplib as http
import logging

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context import RequestContext as Ctx
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.utils import timezone

from ecm import apps, plugins
from ecm.apps.scheduler import process
from ecm.apps.common.models import Setting
from ecm.utils.format import print_time_min
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.views.decorators import check_user_access, basic_auth_required
from ecm.apps.scheduler.models import ScheduledTask


LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@basic_auth_required(username=Setting.get('common_cron_username'))
def trigger_scheduler(request):
    now = timezone.now()
    tasks_to_execute = ScheduledTask.objects.filter(is_active=True,
                                                    is_running=False,
                                                    is_scheduled=False,
                                                    next_execution__lt=now).order_by("-priority")
    if tasks_to_execute:
        tasks_list = list(tasks_to_execute)
        tasks_to_execute.update(is_scheduled=True)
        
        process.run_async(*tasks_list)
        
        return HttpResponse(status=http.ACCEPTED)
    else:
        return HttpResponse(status=http.NOT_MODIFIED)

#------------------------------------------------------------------------------
@check_user_access()
def task_list(request):
    return render_to_response('ecm/scheduler/tasks.html', Ctx(request))

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
    for task in query.order_by('-priority'):
        tasks.append([
            task.function,
            task.next_execution_admin_display(),
            task.frequency_admin_display(),
            print_time_min(task.last_execution),
            task.is_last_exec_success,
            task.is_running,
            task.is_scheduled,
            task.as_html()
        ])

    return datatable_ajax_data(tasks, params.sEcho)



#------------------------------------------------------------------------------
@check_user_access()
def launch_task(request, task_id):
    try:
        task = get_object_or_404(ScheduledTask, pk=int(task_id))
    except ValueError:
        raise Http404()

    if task.is_running or task.is_scheduled:
        code = http.NOT_MODIFIED
        message = 'Task "%s" is already running.' % task.function
    elif not task.is_active:
        code = http.NOT_MODIFIED
        message = 'Task "%s" is disabled.' % task.function
    else:
        code = http.ACCEPTED
        message = ''
        task.is_scheduled = True
        task.save()
        
        process.run_async(task)

    if message:
        LOG.warning(message)

    next_page = request.GET.get("next", None)
    if next_page is not None:
        # we let the task the time to start before redirecting
        # so the "next" web page can display that it is actually running
        time.sleep(0.2)
        return redirect(next_page)
    else:
        return HttpResponse(message, status=code)

