# Copyright (c) 2010-2011 Robin Jarry
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


import json
import re, time
import httplib as http
from datetime import datetime
import logging

from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from ecm.data.roles.models import Member
from ecm.view import extract_datatable_params
from ecm.data.corp.models import Corp
from ecm.view.decorators import basic_auth_required, check_user_access
from ecm.data.scheduler.models import ScheduledTask
from ecm.data.scheduler.threads import TaskThread

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
SHOWINFO_PATTERN = re.compile(r"showinfo:13\d\d//(\d+)", re.IGNORECASE + re.DOTALL)
@login_required
def corp(request):
    try:
        corp = Corp.objects.get(id=1)
        corp.description = SHOWINFO_PATTERN.subn(r"/members/\1", corp.description)[0]
        corp.memberCount = Member.objects.filter(corped=True).count()
    except Corp.DoesNotExist:
        corp = Corp(corporationName="No Corporation info")

    data = { 'corp' : corp }

    return render_to_response("common/corp.html", data, RequestContext(request))


#------------------------------------------------------------------------------
@basic_auth_required(username=settings.CRON_USERNAME)
def trigger_scheduler(request):
    now = datetime.now()
    tasks_to_execute = ScheduledTask.objects.filter(is_active=True, 
                                                    is_running=False,
                                                    next_execution__lt=now).order_by("-priority")
    if tasks_to_execute and not ScheduledTask.objects.filter(is_running=True):
        TaskThread(tasks=tasks_to_execute).start()
        return HttpResponse(status=http.ACCEPTED)
    else:
        logger.warning("Some tasks are already running, skipping scheduler start.")
        return HttpResponse(status=http.NOT_MODIFIED)

#------------------------------------------------------------------------------
@check_user_access()
def task_list(request):
    return render_to_response('common/tasks.html', RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
def task_list_data(request):
    try:
        params = extract_datatable_params(request)
    except:
        return HttpResponseBadRequest()
    
    functions = [ t[0] for t in ScheduledTask.FUNCTION_CHOICES ]
    tasks = []
    for t in ScheduledTask.objects.filter(function__in=functions):
        tasks.append([
            t.get_function_display(),
            t.next_execution_admin_display(),
            t.frequency_admin_display(),
            t.is_running,
            t.as_html(next='/tasks')
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
    except ValueError as e:
        raise HttpResponseBadRequest(str(e))
    
    if task.is_running:
        TaskThread(tasks=[task]).start()
        code = http.ACCEPTED
    else:
        code = http.NOT_MODIFIED
        logger.warning("Task '%s' is already running." % task.function)
    
    next_page = request.GET.get("next", None)
    if next_page is not None:
        # we let the task the time to start before redirecting
        # so the "next" web page can display that it is actually running
        time.sleep(0.2)
        return redirect(next_page)
    else:
        return HttpResponse(status=code)




