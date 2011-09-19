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

__date__ = "2011 8 19"
__author__ = "diabeteman"



from django.http import Http404, HttpResponseBadRequest
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect

from ecm.data.industry.models import Order
from ecm.data.industry.models.catalog import CatalogEntry


#------------------------------------------------------------------------------
@login_required
def new(request):
    return render_to_response('industry/order_create.html', {}, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def create(request):
    items, valid_order = extract_order_items(request)

    if valid_order:
        order = Order.objects.create(originator=request.user, pricing_id=1)
        order.modify(items)
        return redirect('/industry/orders/%d' % order.id)
    else:
        return render_to_response('industry/order_create.html', {'items': items}, RequestContext(request))

#------------------------------------------------------------------------------
@login_required
def details(request, order_id):
    try:
        order = get_object_or_404(Order, id=int(order_id))
    except ValueError:
        raise Http404()

    logs = order.logs.all().order_by('-date')

    data = {'order' : order, 'logs': logs}

    return render_to_response('industry/order_details.html', data, RequestContext(request))



#------------------------------------------------------------------------------
@login_required
def modify(request, order_id):

    try:
        order = get_object_or_404(Order, id=int(order_id))
    except ValueError:
        raise Http404()

    if request.method == 'GET':
        return render_to_response('industry/order_modify.html', {'order': order}, RequestContext(request))
    elif request.method == 'POST':
        items, valid_order = extract_order_items(request)
        if valid_order:
            order.modify(items)
            return redirect('/industry/orders/%d' % order.id)
        else:
            return redirect('/industry/orders/%d/modify' % order.id)
    else:
        return HttpResponseBadRequest()





def extract_order_items(request):
    items = []
    valid_order = True
    for key, value in request.POST.items():
        try:
            typeID = int(key)
            quantity = int(value)
            item = CatalogEntry.objects.get(typeID=typeID)
            items.append( (item, quantity) )
        except ValueError:
            pass
        except CatalogEntry.DoesNotExist:
            valid_order = False
    return items, valid_order