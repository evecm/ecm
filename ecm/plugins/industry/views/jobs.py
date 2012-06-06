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

__date__ = '2011 8 19'
__author__ = 'diabeteman'

import logging

from django.http import  HttpResponseBadRequest, HttpResponse
from django.template.context import RequestContext as Ctx
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.db import transaction

from ecm.apps.eve.models import Type
from ecm.views.decorators import check_user_access
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.plugins.industry.models import Job
from ecm.utils.format import print_duration, print_integer
from ecm.plugins.industry.models.order import IllegalTransition

LOG = logging.getLogger(__name__)

COLUMNS = [
    ['#', 'id'],
    ['State', 'state'],
    ['Action', None],
    ['Order', 'order'],
    ['Assignee', 'assignee'],
    ['Duration', 'duration'],
    ['Activity', 'activity'],
    ['Quantity/Runs', 'runs'],
    ['Item', 'item_id'],
]
#------------------------------------------------------------------------------
@check_user_access()
def jobs_list(request):
    activities = Job.ACTIVITIES.items()
    data = {
        'columns' : [ col[0] for col in COLUMNS ],
        'states': Job.STATES,
        'activities': activities,
        'activity': 'all',
        'state': 'all',
        'assignment': 'unassigned',
    }
    return render_to_response('ecm/industry/jobs_list.html', data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def jobs_list_data(request):
    try:
        params = extract_datatable_params(request)
        activity = getattr(request, request.method)['activity']
        try:
            activity = int(activity)
        except ValueError:
            pass
        state = getattr(request, request.method)['state']
        try:
            state = int(state)
        except ValueError:
            pass
        assignment = getattr(request, request.method)['assignment']
    except (KeyError, ValueError), e:
        return HttpResponseBadRequest(str(e))

    query = Job.objects.all()

    total = query.count()
    if activity != 'all':
        query = query.filter(activity=activity)
    if state != 'all':
        query = query.filter(state=int(state))
    if assignment == 'me':
        query = query.filter(assignee=request.user)
    elif assignment == 'unassigned':
        query = query.filter(assignee__isnull=True)

    if params.search:
        matching_items = Type.objects.filter(typeName__icontains=params.search)
        matching_ids = list(matching_items.values_list('typeID', flat=True)[:100])
        search_args = Q(assignee__username__icontains=params.search)
        search_args |= Q(item_id__in=matching_ids)
        query = query.filter(search_args).distinct()

    filtered = query.count()
    data = []
    for job in query[params.first_id:params.last_id]:
        if job.duration:
            duration = print_duration(job.duration, verbose=False)
        else:
            duration = '-'
        activity_icon = '<img src="%sindustry/img/%s.png" title="%s"/>' % (settings.STATIC_URL,
                                                                           job.activity_text.lower(),
                                                                           job.activity_text)
        data.append([
            'Job #%d' % job.id,
            job.state,
            job.id,
            job.order.permalink(shop=False),
            job.assignee_permalink(),
            duration,
            activity_icon,
            print_integer(round(job.runs)),
            job.item.typeName,
        ])

    return datatable_ajax_data(data, params.sEcho, total, filtered)

#------------------------------------------------------------------------------
@transaction.commit_on_success
@check_user_access()
def change_state(request, job_id, action):
    try:
        job = get_object_or_404(Job, pk=int(job_id))
    except ValueError, e:
        return HttpResponseBadRequest(str(e))

    if action == 'start':
        job.state = Job.IN_PRODUCTION
        job.assignee = request.user
        job.save()
        job.children_jobs.filter(state=Job.PENDING).update(assignee=request.user, state=Job.IN_PRODUCTION)
        try:
            if job.order is not None:
                job.order.start_preparation(user=request.user)
        except IllegalTransition:
            pass
        return HttpResponse()
    elif action == 'done':
        job.state = Job.READY
        job.save()
        job.children_jobs.exclude(state=Job.READY).update(assignee=request.user, state=Job.READY)
        try:
            if job.order is not None and not job.order.jobs.exclude(state=Job.READY):
                job.order.end_preparation(request.user)
        except IllegalTransition:
            pass
        return HttpResponse()
    else:
        return HttpResponseBadRequest('Transition not allowed "%s"' % action)


