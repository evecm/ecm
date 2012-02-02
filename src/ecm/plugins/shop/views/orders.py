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

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.template.context import RequestContext as Ctx
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.utils.text import truncate_words

from ecm.views import extract_datatable_params
from ecm.core import utils
from ecm.views.decorators import forbidden
from ecm.plugins.industry.models.order import Order, IllegalTransition
from ecm.plugins.industry.views.orders import extract_order_items

#------------------------------------------------------------------------------
COLUMNS = [
    ['#', 'id'],
    ['State', 'stateText'],
    ['Items', None],
    ['Quote', 'quote'],
]
@login_required
def myorders(request):
    columns = [ col[0] for col in COLUMNS ]
    return render_to_response('shop_myorders.html', {'columns' : columns}, Ctx(request))

#------------------------------------------------------------------------------
@login_required
def myorders_data(request):
    try:
        params = extract_datatable_params(request)
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    query = Order.objects.filter(originator=request.user).select_related(depth=3)

    order_count = query.count()
    if params.search:
        query = query.filter(rows__catalogEntry__typeName__icontains=params.search)
    filtered_count = query.count()

    orders = []
    for order in query[params.first_id:params.last_id]:
        items = [ row.catalogEntry.typeName for row in order.rows.all() ]
        orders.append([
            order.permalink(),
            order.stateText(),
            truncate_words(', '.join(items), 6),
            utils.print_float(order.quote) + ' ISK',
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : order_count,
        "iTotalDisplayRecords" : filtered_count,
        "aaData" : orders
    }

    return HttpResponse(json.dumps(json_data), mimetype='text/json')
#------------------------------------------------------------------------------
@login_required
def create(request):
    if request.method == 'POST':
        items, valid_order = extract_order_items(request)
        if valid_order:
            order = Order.objects.create(originator=request.user, pricing_id=1)
            order.modify(items)
            return redirect('/shop/orders/%d/' % order.id)
    else:
        items = []

    return render_to_response('shop_order.html', {'items': items}, Ctx(request))

#------------------------------------------------------------------------------
@login_required
def details(request, order_id):
    try:
        order = get_object_or_404(Order, id=int(order_id))
    except ValueError:
        raise Http404()

    if order.originator != request.user and not request.user.is_superuser:
        return forbidden(request)

    logs = order.logs.all().order_by('-date')
    validTransitions = [ (trans.__name__, trans.text) 
                               for trans in order.getValidTransitions(customer=True) ]

    data = {'order' : order, 'logs': logs, 'validTransitions' : validTransitions}

    return render_to_response('shop_order_details.html', data, Ctx(request))

#------------------------------------------------------------------------------
@login_required
def change_state(request, order_id, transition):
    try:
        order = get_object_or_404(Order, id=int(order_id))
        order.checkCanPassTransition(transition)
        
        if request.user != order.originator:
            return forbidden(request)

        if transition == order.modify.__name__:
            return modify(request, order)
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
    except IllegalTransition, e:
        logs = order.logs.all().order_by('-date')
        validTransitions = [ (trans.__name__, trans.text) 
                                   for trans in order.getValidTransitions(customer=True) ]
    
        data = {'order' : order, 'logs': logs, 'validTransitions' : validTransitions, 'error': e}
    
        return render_to_response('shop_order_details.html', data, Ctx(request))
    

#------------------------------------------------------------------------------
def modify(request, order):
    if request.method == 'POST':
        items, valid_order = extract_order_items(request)
        if valid_order:
            order.modify(items)
            return redirect('/shop/orders/%d/' % order.id)
    return render_to_response('shop_order.html', {'order': order}, Ctx(request))
    
