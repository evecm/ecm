# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-05-16"
__author__ = "diabeteman"


from django.shortcuts import render_to_response, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from ecm.data.corp.models import Corp
from ecm.core.auth import basic_auth_required
from ecm.data.scheduler.models import ScheduledTask
from ecm.data.scheduler.threads import TaskThread

import re
import httplib as http
from datetime import datetime
from ecm import settings
import time

SHOWINFO_PATTERN = re.compile(r"showinfo:1383//(\d+)", re.IGNORECASE + re.DOTALL)

#------------------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return render_to_response("common/login.html")
#------------------------------------------------------------------------------
@login_required
@csrf_protect
def corp(request):
    try:
        corp = Corp.objects.get(id=1)
        corp.description = re.subn(SHOWINFO_PATTERN, r"/members/\1", corp.description)[0]
    except ObjectDoesNotExist:
        corp = Corp(corporationName="No Corporation info")

    data = { 'corp' : corp }

    return render_to_response("common/corp.html", data, context_instance=RequestContext(request))


#------------------------------------------------------------------------------
@basic_auth_required(username=settings.CRON_USERNAME)
def trigger_scheduler(request):
    try:
        now = datetime.now()
        tasks_to_execute = ScheduledTask.objects.filter(is_active=True, 
                                                        is_running=False,
                                                        next_execution__lt=now).order_by("-priority")
        if tasks_to_execute.count():
            TaskThread(tasks=tasks_to_execute).start()
            return HttpResponse(status=http.ACCEPTED)
        else:
            return HttpResponse(status=http.NOT_MODIFIED)
    except Exception, e:
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        return HttpResponse(content="".join(errortrace), status=http.INTERNAL_SERVER_ERROR)

def task_list(request):
    return render_to_response("common/taks_list.html")

#------------------------------------------------------------------------------
@basic_auth_required(username=settings.CRON_USERNAME)
def launch_task(request, function):
    try:
        try:
            task = ScheduledTask.objects.get(function=function)
        except ObjectDoesNotExist:
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
        
    except Exception, e:
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        return HttpResponse(content="".join(errortrace), status=http.INTERNAL_SERVER_ERROR)
