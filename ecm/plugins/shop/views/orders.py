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

__date__ = "2011 11 12"
__author__ = "diabeteman"

import logging

from django.template.context import RequestContext as Ctx
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import Http404, HttpResponseBadRequest
from django.utils.text import truncate_words

from ecm.utils.format import print_float, print_time_min, verbose_name
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.plugins.shop.views.utils import extract_order_items
from ecm.views.decorators import forbidden, check_user_access
from ecm.plugins.industry.models.order import Order, IllegalTransition

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
COLUMNS = [
    ['#', 'id'],
    ['State', 'state'],
    ['Items', None],
    ['Quote', 'quote'],
    ['Creation Date', None],
]
@check_user_access()
def myorders(request):
    """
    Serves URL /shop/orders/
    """
    columns = [ col[0] for col in COLUMNS ]
    return render_to_response('ecm/shop/shop_myorders.html', {'columns' : columns}, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def myorders_data(request):
    """
    Serves URL /shop/orders/data/ (jQuery datatables plugin)
    """
    try:
        params = extract_datatable_params(request)
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    query = Order.objects.filter(originator=request.user).select_related(depth=3)

    order_count = query.count()
    if params.search:
        query = query.filter(rows__catalog_entry__typeName__icontains=params.search)
    filtered_count = query.count()

    if params.column not in (0, 1, 3):
        params.column = 0 # by default, show latest orders first
    sort_col = COLUMNS[params.column][1]
    if not params.asc:
        sort_col = '-' + sort_col

    query = query.order_by(sort_col)

    orders = []
    for order in query[params.first_id:params.last_id]:
        items = [ row.catalog_entry.typeName for row in order.rows.all() ]
        orders.append([
            order.permalink(),
            order.state_text(),
            truncate_words(', '.join(items), 6),
            print_float(order.quote) + ' ISK',
            print_time_min(order.creation_date()),
        ])

    return datatable_ajax_data(data=orders, echo=params.sEcho,
                               total=order_count, filtered=filtered_count)

#------------------------------------------------------------------------------
@check_user_access()
def create(request):
    """
    Serves URL /shop/orders/create/
    """
    if request.method == 'POST':
        items, valid_order = extract_order_items(request)
        if valid_order:
            order = Order.objects.create(originator=request.user)
            order.modify(items)
            return redirect('/shop/orders/%d/' % order.id)
    else:
        items = []

    return render_to_response('ecm/shop/shop_order.html', {'items': items}, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def details(request, order_id):
    """
    Serves URL /shop/orders/<order_id>/
    """
    try:
        order = get_object_or_404(Order, id=int(order_id))
    except ValueError:
        raise Http404()

    if order.originator != request.user:
        return forbidden(request)

    return _order_details(request, order)


#------------------------------------------------------------------------------
@check_user_access()
def add_comment(request, order_id):
    """
    Serves URL /shop/orders/<order_id>/comment/
    """
    try:
        order = get_object_or_404(Order, id=int(order_id))
    except ValueError:
        raise Http404()

    if order.originator != request.user:
        return forbidden(request)

    if request.method == 'POST':
        comment = request.POST.get('comment', '')
        order.add_comment(request.user, comment)
        LOG.info('"%s" added a comment on order #%d', request.user, order.id)

    return redirect('/shop/orders/%d/' % order.id)

#------------------------------------------------------------------------------
@check_user_access()
def change_state(request, order_id, transition):
    """
    Serves URL /shop/orders/<order_id>/<transition>/
    """
    try:
        order = get_object_or_404(Order, id=int(order_id))

        if request.user != order.originator:
            return forbidden(request)

        order.check_can_pass_transition(transition)

        if transition == order.modify.__name__:
            return _modify(request, order)
        elif transition == order.confirm.__name__:
            order.confirm()
            return redirect('/shop/orders/%d/' % order.id)
        elif transition == order.cancel.__name__:
            comment = request.POST.get('comment', None)
            if not comment:
                raise IllegalTransition('Please leave a comment.')
            order.cancel(comment)
            return redirect('/shop/orders/%d/' % order.id)
        else:
            return forbidden(request)
    except ValueError:
        raise Http404()
    except IllegalTransition, error:
        return _order_details(request, order, error)

#------------------------------------------------------------------------------
def _order_details(request, order, error=None):
    logs = order.logs.all().order_by('-date')
    valid_transitions = [(trans.__name__, verbose_name(trans))
                         for trans in order.get_valid_transitions(customer=True)]
    data = {
        'order': order,
        'logs': logs,
        'valid_transitions': valid_transitions,
        'states': Order.STATES.items(),
        'error': error,
    }

    return render_to_response('ecm/shop/shop_order_details.html', data, Ctx(request))

#------------------------------------------------------------------------------
def _modify(request, order):
    """
    This should only be accessible through the change_state() function.
    """
    if request.method == 'POST':
        items, valid_order = extract_order_items(request)
        if valid_order:
            order.modify(items)
            return redirect('/shop/orders/%d/' % order.id)
    return render_to_response('ecm/shop/shop_order.html', {'order': order}, Ctx(request))

