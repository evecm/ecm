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
from ecm.plugins.industry.models.catalog import CatalogEntry

__date__ = "2011 11 12"
__author__ = "diabeteman"

import re
try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.template.context import RequestContext
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
    ['Delivery Date', 'deliveryDate'],
    ['Items', None],
    ['Quote', 'quote'],
]
@login_required
def myorders(request):
    columns = [ col[0] for col in COLUMNS ]
    return render_to_response('shop_myorders.html', {'columns' : columns}, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def myorders_data(request):
    try:
        params = extract_datatable_params(request)
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    query = Order.objects.filter(originator=request.user)

    orders = []
    for order in query:
        items = [ row.catalogEntry.typeName for row in order.rows.all() ]
        if order.deliveryDate is not None:
            delivDate = utils.print_date(order.deliveryDate)
        else:
            delivDate = '(none)'
        orders.append([
            order.permalink,
            order.stateText,
            delivDate,
            truncate_words(', '.join(items), 6),
            utils.print_float(order.quote),
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : len(orders),
        "iTotalDisplayRecords" : len(orders),
        "aaData" : orders
    }

    return HttpResponse(json.dumps(json_data))
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

    return render_to_response('shop_createorder.html', {'items': items}, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def details(request, order_id):
    try:
        order = get_object_or_404(Order, id=int(order_id))
    except ValueError:
        raise Http404()

    logs = order.logs.all().order_by('-date')
    validTransitions = [ (trans.id, trans.text) for trans in order.validTransitions ]


    data = {'order' : order, 'logs': logs, 'validTransitions' : validTransitions}

    return render_to_response('order_details.html', data, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def change_state(request, order_id, transition):
    try:
        order = get_object_or_404(Order, id=int(order_id))
        order.checkCanPassTransition(transition)
        if request.user != order.originator:
            return forbidden(request)
    except ValueError:
        raise Http404()
    except IllegalTransition, e:
        data = {'order':order, 'err': e}
        return render_to_response('shop_illegaltransition.html', data, RequestContext(request))




#------------------------------------------------------------------------------
HEADER = re.compile(r'\[(?P<ship>.+),.*')
ITEM = re.compile(r'^(?P<item>\w[^,\n]+)(,\s+(?P<charge>(.*)))?$', re.MULTILINE)
STACK = re.compile(r'(.*)\s+x(\d+)')
def allFittingItems(eftExport):
    all_items = {}
    match = HEADER.search(eftExport)
    if match:
        all_items[match.groupdict()['ship']] = 1
    for match in ITEM.finditer(eftExport):
        item = match.groupdict()['item'].strip()

        match_stack = STACK.search(item)
        if match_stack:
            item = match_stack.group(1)
            stack = int(match_stack.group(2))
        else:
            stack = 1

        if all_items.has_key(item):
            all_items[item] += stack
        else:
            all_items[item] = stack

        if match.groupdict()['charge'] is not None:
            charge = match.groupdict()['charge']
            if all_items.has_key(charge):
                all_items[charge] += 1
            else:
                all_items[charge] = 1
    return all_items



#------------------------------------------------------------------------------
@login_required
def create_from_eft(request):
    if request.method == 'POST':
        try:
            eftBlock = request.POST['eftBlock'].replace('\r\n', '\n')
            items_dict = allFittingItems(eftBlock)
            query = CatalogEntry.objects.filter(typeName__in=items_dict.keys(), isAvailable=True)
            items = [ (i, items_dict[i.typeName]) for i in query ]
            return render_to_response('shop_createorder.html', {'items': items}, RequestContext(request))
        except:
            pass
    return render_to_response('shop_createorder_eft.html', {}, RequestContext(request))




