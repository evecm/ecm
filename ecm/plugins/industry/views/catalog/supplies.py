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

__date__ = "2011 11 19"
__author__ = "diabeteman"

import logging

from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.template.context import RequestContext as Ctx
from django.shortcuts import get_object_or_404, render_to_response

from ecm.utils import _json as json
from ecm.utils.format import print_time_min, print_float
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.views.decorators import check_user_access
from ecm.plugins.industry.tasks import evecentral
from ecm.plugins.industry.models import SupplySource, Supply, PriceHistory
from ecm.plugins.industry import constants as C

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
COLUMNS = [
    'Item',
    'Price',
    'Auto Update',
    'Supply Source',
]
FILTERS = [
    ('All', 'all', None),
    ('Base Minerals', 'minerals', C.BASE_MINERALS),
    ('Composites', 'composites', C.COMPOSITE_MATERIALS),
    ('Datacores', 'datacores', C.DATACORES),
    ('Decryptors', 'decryptors', C.DECRYPTORS),
    ('Salvage', 'salvage', C.SLAVAGE),
    ('Ice Products', 'ice', C.ICE_PRODUCTS),
    ('Planetary', 'planetary', C.PLANETARY_MATERIALS),
    ('Misc', 'misc', None),
]
@check_user_access()
def supplies(request):
    """
    Serves URL /industry/catalog/supplies/
    """
    data = {
        'supply_sources': SupplySource.objects.all(),
        'columns': COLUMNS,
        'filters': FILTERS,
    }
    return render_to_response('ecm/industry/catalog/supplies.html', data, Ctx(request))


#------------------------------------------------------------------------------
MISC_ITEMS = (C.BASE_MINERALS +
              C.COMPOSITE_MATERIALS +
              C.DATACORES +
              C.DECRYPTORS +
              C.ICE_PRODUCTS +
              C.SLAVAGE +
              C.PLANETARY_MATERIALS)
@check_user_access()
def supplies_data(request):
    """
    Serves URL /industry/catalog/supplies/data/
    """
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.displayMode = REQ.get('displayMode', 'all')
        params.filter = REQ.get('filter', 'all')
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    query = Supply.objects.all().order_by('typeID')
    if params.displayMode == 'auto':
        query = query.filter(auto_update=True)
    elif params.displayMode == 'manual':
        query = query.filter(auto_update=False)

    if params.filter == 'misc':
        query = query.exclude(typeID__in=MISC_ITEMS)
    elif params.filter == 'all':
        pass
    else:
        typeIDs = []
        for _, key, ids in FILTERS:
            if key == params.filter:
                typeIDs = ids
                break
        query = query.filter(typeID__in=typeIDs)

    query = list(query)
    if params.search:
        total_items = len(query)
        query = [ bp for bp in query if params.search.lower() in bp.typeName.lower() ]
        filtered_items = len(query)
    else:
        total_items = filtered_items = len(query)

    items = []
    for i in query[params.first_id:params.last_id]:
        items.append([
            i.permalink,
            print_float(i.price),
            bool(i.auto_update),
            i.supply_source.location_id,
            i.typeID,
        ])

    return datatable_ajax_data(data=items, echo=params.sEcho,
                               total=total_items, filtered=filtered_items)

#------------------------------------------------------------------------------
DETAILS_COLUMNS = ['Date', 'Price']
@check_user_access()
def details(request, supply_id):
    """
    Serves URL /industry/catalog/supplies/<supply_id>/
    """
    try:
        supply = get_object_or_404(Supply, typeID=int(supply_id))
    except ValueError:
        raise Http404()
    data = {
        'supply': supply,
        'supply_sources': SupplySource.objects.all(),
        'columns': DETAILS_COLUMNS,
    }
    return render_to_response('ecm/industry/catalog/supply_details.html', data, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def details_data(request, supply_id):
    """
    Serves URL /industry/catalog/supplies/<supply_id>//data/
    """
    try:
        params = extract_datatable_params(request)
        supply_id = int(supply_id)
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    query = PriceHistory.objects.filter(supply=supply_id)

    histories = []
    for history in query[params.first_id:params.last_id]:
        histories.append([
            print_time_min(history.date),
            print_float(history.price),
        ])

    return datatable_ajax_data(data=histories, echo=params.sEcho)

#------------------------------------------------------------------------------
@check_user_access()
def update_price(request, supply_id):
    """
    Serves URL /industry/catalog/supplies/<supply_id>/updateprice/
    """
    try:
        supply = get_object_or_404(Supply, typeID=int(supply_id))
    except ValueError:
        raise Http404()
    buyPrices = evecentral.get_buy_prices([supply.typeID], supply.supply_source_id)
    if buyPrices[supply.typeID] > 0.0 and supply.price != buyPrices[supply.typeID]:
        supply.update_price(buyPrices[supply.typeID])
        logger.info('"%s" updated price for supply "%s" (%s -> %s)' % (request.user,
                                                                supply.typeName,
                                                                supply.supply_source,
                                                                print_float(supply.price)))
    return HttpResponse(print_float(supply.price))

#------------------------------------------------------------------------------
@check_user_access()
def info(request, attr):
    """
    Serves URL /industry/catalog/supplies/<attr>/

    must have "id" and "value" parameters in the request
    if request is POST:
        update supply.attr with value
    return the supply.attr as JSON
    """
    try:
        item_id = getattr(request, request.method)['id']
        supply = get_object_or_404(Supply, typeID=int(item_id))
        displayVal = getattr(supply, attr)
    except KeyError:
        return HttpResponseBadRequest('Missing "id" parameter')
    except (ValueError, AttributeError):
        raise Http404()

    if request.method == 'POST':
        try:
            value = json.loads(request.POST['value'])
            if type(value) == type(getattr(supply, attr)):
                if attr == 'price':
                    supply.update_price(value)
                    displayVal = print_float(value)
                else:
                    setattr(supply, attr, value)
                    supply.save()
                    displayVal = value
                logger.info('"%s" changed supply "%s" (%s -> %s)' % (request.user,
                                                                     supply.typeName,
                                                                     attr, displayVal))
        except KeyError:
            return HttpResponseBadRequest('Missing "value" parameter')
        except ValueError:
            return HttpResponseBadRequest('Cannot parse "value" parameter')

    return HttpResponse(str(displayVal))
