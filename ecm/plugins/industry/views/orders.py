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

__date__ = "2011 8 19"
__author__ = "diabeteman"

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

from ecm.utils.format import print_date, print_float, print_integer, verbose_name
from ecm.views.decorators import check_user_access, forbidden
from ecm.plugins.industry.models.order import IllegalTransition
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.plugins.industry.models import Order

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
COLUMNS = [
    ['#', 'id'],
    ['State', 'state'],
    ['Originator', 'originator'],
    ['Client', 'client'],
    ['Delivery Date', 'delivery_date'],
    ['Items', None],
    ['Quote', 'quote'],
]
@login_required
def orders(request):
    columns = [ col[0] for col in COLUMNS ]
    return render_to_response('orders_list.html',
                              {'columns' : columns,
                               'states': Order.STATES},
                              Ctx(request))

#------------------------------------------------------------------------------
@login_required
def orders_data(request):
    try:
        params = extract_datatable_params(request)
    except Exception, e:
        return HttpResponseBadRequest(str(e))
    try:
        states = [int(x) for x in request.GET.get('states').split(',')]
    except ValueError:
        states = []

    query = Order.objects.filter(state__in= states)

    sort_by = COLUMNS[params.column][1]

    if not params.asc:
        sort_by = '-' + sort_by

    query = query.order_by(sort_by)

    orders = []
    for order in query[params.first_id:params.last_id]:
        items = [ row.catalog_entry.typeName for row in order.rows.all() ]
        if order.delivery_date is not None:
            delivDate = print_date(order.delivery_date)
        else:
            delivDate = '(none)'
        orders.append([
            order.permalink(shop=False),
            order.state_text(),
            order.originator_permalink(),
            order.client or '(none)',
            delivDate,
            truncate_words(', '.join(items), 6),
            print_float(order.quote) + ' ISK',
        ])

    return datatable_ajax_data(data=orders, echo=params.sEcho)

#------------------------------------------------------------------------------
@check_user_access()
def details(request, order_id):
    """
    Serves URL /industry/orders/<order_id>/
    """
    try:
        order = get_object_or_404(Order, id=int(order_id))
    except ValueError:
        raise Http404()

    return _order_details(request, order)

#------------------------------------------------------------------------------
@transaction.commit_on_success
@check_user_access()
def change_state(request, order_id, transition):
    """
    Serves URL /industry/orders/<order_id>/<transition>/
    """
    try:
        order = get_object_or_404(Order, id=int(order_id))

        order.check_can_pass_transition(transition)

        if transition == order.accept.__name__:
            if order.accept(request.user):
                return redirect('/industry/orders/%d/' % order.id)
            else:
                raise IllegalTransition('Order could not be accepted. See order log for details.')
        elif transition == order.confirm.__name__:
            order.confirm()
            return redirect('/industry/orders/%d/' % order.id)
        elif transition == order.cancel.__name__:
            comment = request.POST.get('comment', None)
            if not comment:
                raise IllegalTransition('Please leave a comment.')
            order.cancel(comment)
            return redirect('/industry/orders/%d/' % order.id)
        else:
            return forbidden(request)
    except ValueError:
        raise Http404()
    except IllegalTransition, error:
        return _order_details(request, order, error)

#------------------------------------------------------------------------------
@check_user_access()
def add_comment(request, order_id):
    """
    Serves URL /industry/orders/<order_id>/comment/
    """
    try:
        order = get_object_or_404(Order, id=int(order_id))
    except ValueError:
        raise Http404()

    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        order.add_comment(request.user, comment)
        LOG.info('"%s" added a comment on order #%d', request.user, order.id)

    return redirect('/industry/orders/%d/' % order.id)

#------------------------------------------------------------------------------
def _order_details(request, order, error=None):
    logs = order.logs.all().order_by('-date')
    valid_transitions = [(trans.__name__, verbose_name(trans))
                         for trans in order.get_valid_transitions(customer=False)]

    # we get the 1st jobs associated to this order's rows
    jobs = order.jobs.select_related(depth=2).filter(parent_job__isnull=True)

    data = {
        'order': order,
        'logs': logs,
        'valid_transitions': valid_transitions,
        'states': Order.STATES.items(),
        'error': error,
        'jobs_tree': json.dumps(_build_jobs_tree(jobs)),
    }

    return render_to_response('order_details.html', data, Ctx(request))

#------------------------------------------------------------------------------
JOB_SPAN = '<span class="industry-job" title="%s"><strong>%s</strong> - x <i>%s</i></span>'
def _build_jobs_tree(jobs):
    jobs_tree = []
    for job in jobs:
        json_job = {
            'data': JOB_SPAN % (job.activity_text,
                                job.item.typeName,
                                print_integer(job.runs)),
            'attr': {'rel': job.activity_text.lower()},
        }
        if job.children_jobs.all():
            json_job['children'] = _build_jobs_tree(job.children_jobs.all())
        jobs_tree.append(json_job)
    return jobs_tree

