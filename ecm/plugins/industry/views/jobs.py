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
from ecm.apps.eve.models import Type

__date__ = '2011 8 19'
__author__ = 'diabeteman'

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json
import logging

from django.db import transaction
from django.http import Http404, HttpResponseBadRequest
from django.template.context import RequestContext as Ctx
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.utils.text import truncate_words
from django.db.models import Q

from ecm.views.decorators import check_user_access, forbidden
from ecm.plugins.industry.models.order import IllegalTransition
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.core import utils
from ecm.plugins.industry.models import Job

LOG = logging.getLogger(__name__)

COLUMNS = [
    ['#', 'id'],
    ['State', 'state'],
    ['Order', 'order'],
    ['Owner', 'owner'],
    ['Duration', 'duration'],
    ['Activity', 'activity'],
    ['Quantity/Runs', 'runs'],
    ['Item', 'item_id'],
]

@check_user_access()
def jobs_list(request):
    data = {
        'columns' : [ col[0] for col in COLUMNS ],
        'states': Job.STATES,
        'state': 'all',
        'owner': 'all',
    }
    return render_to_response('jobs_list.html', data, Ctx(request))


@check_user_access()
def jobs_list_data(request):
    try:
        params = extract_datatable_params(request)
        state = getattr(request, request.method)['state']
        owner = getattr(request, request.method)['owner']
    except (KeyError, ValueError), e:
        return HttpResponseBadRequest(str(e))
    
    query = Job.objects.all()
    
    total = query.count()
    
    if owner == 'mine':
        query = query.filter(owner=request.user)
    
    if state != 'all':
        query = query.filter(state=int(state))
    
    if params.search:
        matching_items = Type.objects.filter(typeName__icontains=params.search)
        matching_ids = list(matching_items.values_list('typeID', flat=True))
        search_args = Q(owner__username__icontains=params.search)
        search_args |= Q(item_id__in=matching_ids)
        query = query.filter(search_args)
    
    filtered = query.count()
    data = []
    for job in query[params.first_id:params.last_id]:
        
        if job.duration:
            duration = utils.print_duration(job.duration, verbose=False)
        else:
            duration = '-'
        data.append([
            job.permalink(),
            job.state_text,
            job.order.permalink(shop=False),
            job.owner_permalink(),
            duration,
            job.activity_text,
            utils.print_integer(round(job.runs)),
            job.item.typeName,
        ])
    
    return datatable_ajax_data(data, params.sEcho, total, filtered)
    
    