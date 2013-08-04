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

__date__ = "2012 2 2"
__author__ = "diabeteman"

from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse, \
    HttpResponseNotFound

from ecm.utils import _json as json
from ecm.views import JSON
from ecm.apps.common import eft
from ecm.views.decorators import check_user_access
from ecm.plugins.industry.models import CatalogEntry, PricingPolicy

#------------------------------------------------------------------------------
@check_user_access()
def parse_eft(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()

    eft_block = request.POST.get('eft_block', None)
    if not eft_block:
        return HttpResponseBadRequest('Empty EFT block')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError, e:
        return HttpResponseBadRequest(str(e))

    eft_items = eft.parse_export(eft_block)

    query = CatalogEntry.objects.filter(typeName__in=eft_items.keys(), is_available=True)
    items = []
    for item in query:
        if item.fixed_price is not None:
            price = item.fixed_price
        else:
            cost = item.production_cost or 0.0
            surcharge = PricingPolicy.resolve_surcharge(item, request.user, cost)
            price = cost + surcharge
        items.append({
            'typeID': item.typeID,
            'typeName': item.typeName,
            'quantity': eft_items[item.typeName] * quantity,
            'price': price
        })
        eft_items.pop(item.typeName) # we remove the item from the list

    for typeName, _ in eft_items.items():
        # we add the missing items to inform the user
        items.append({
            'typeID': 0,
            'typeName': typeName,
            'quantity': 0,
            'price': None
        })
    return HttpResponse(json.dumps(items), mimetype=JSON)

#------------------------------------------------------------------------------
def extract_order_items(request):
    items = []
    valid_order = True
    for key, value in request.POST.items():
        try:
            typeID = int(key)
            quantity = int(value)
            item = CatalogEntry.objects.get(typeID=typeID)
            if item.is_available:
                items.append((item, quantity))
            else:
                valid_order = False
        except ValueError:
            pass
        except CatalogEntry.DoesNotExist:
            valid_order = False
    return items, valid_order

#------------------------------------------------------------------------------
@check_user_access()
def search_item(request):
    querystring = request.GET.get('q', None)
    try:
        limit = int(request.GET.get('limit', "10"))
    except ValueError:
        limit = 10
    if querystring is not None:
        query = CatalogEntry.objects.filter(typeName__icontains=querystring)
        query = query.filter(is_available=True).order_by('typeName')
        matches = query[:limit].values_list('typeName', flat=True)
        return HttpResponse('\n'.join(matches))
    else:
        return HttpResponseBadRequest('Missing "q" parameter.')

#------------------------------------------------------------------------------
@check_user_access()
def get_item_id(request):
    querystring = request.GET.get('q', None)
    if querystring is not None:
        query = CatalogEntry.objects.filter(typeName__iexact=querystring)
        if query.filter(is_available=True).exists():
            
            item = query[0]
            
            if item.fixed_price is not None:
                price = item.fixed_price
            else:
                cost = item.production_cost or 0.0
                surcharge = PricingPolicy.resolve_surcharge(item, request.user, cost)
                price = cost + surcharge
            
            return HttpResponse(json.dumps([item.typeID, item.typeName, price]), mimetype=JSON)
        else:
            return HttpResponseNotFound('Item <em>%s</em> not available in the shop.' % querystring)
    else:
        return HttpResponseBadRequest('Missing "q" parameter.')
