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


import re, time
import httplib as http
from datetime import datetime

from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.http import HttpResponse

from ecm.data.roles.models import Member
from ecm.data.corp.models import Corp
from ecm.view.decorators import basic_auth_required
from ecm.data.scheduler.models import ScheduledTask
from ecm.data.scheduler.threads import TaskThread

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

    return render_to_response("common/corp.html", data, context_instance=RequestContext(request))


#------------------------------------------------------------------------------
@basic_auth_required(username=settings.CRON_USERNAME)
def trigger_scheduler(request):
    now = datetime.now()
    tasks_to_execute = ScheduledTask.objects.filter(is_active=True, 
                                                    is_running=False,
                                                    next_execution__lt=now).order_by("-priority")
    if tasks_to_execute.count():
        TaskThread(tasks=tasks_to_execute).start()
        return HttpResponse(status=http.ACCEPTED)
    else:
        return HttpResponse(status=http.NOT_MODIFIED)

#------------------------------------------------------------------------------
@basic_auth_required(username=settings.CRON_USERNAME)
def launch_task(request, function):
    try:
        task = ScheduledTask.objects.get(function=function)
    except ScheduledTask.DoesNotExist:
        return HttpResponse(status=http.NOT_FOUND)
    
    if not task.is_running:
        TaskThread(tasks=[task]).start()
        code = http.ACCEPTED
    else:
        code = http.NOT_MODIFIED
    
    next = request.GET.get("next", None)
    if next:
        # we let the task the time to start before redirecting
        # so the "next" web page can display that it is actually running
        time.sleep(0.2)
        return redirect(next)
    else:
        return HttpResponse(status=code)
