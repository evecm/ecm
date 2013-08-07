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

__date__ = "2011 11 13"
__author__ = "diabeteman"


import logging

from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.template.context import RequestContext as Ctx
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render_to_response

from ecm.utils import db
from ecm.utils import _json as json
from ecm.utils.format import print_float
from ecm.apps.common.models import Setting
from ecm.apps.eve.models import Type
from ecm.plugins.industry.models.order import OrderCannotBeFulfilled
from ecm.plugins.industry.models.inventory import Supply
from ecm.views import extract_datatable_params, datatable_ajax_data, JSON
from ecm.views.decorators import check_user_access
from ecm.plugins.industry.models.catalog import CatalogEntry
from ecm.plugins.industry.tasks.industry import update_production_cost
from ecm.plugins.industry.tasks import evecentral

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
COLUMNS = [
    ['Item', 'typeName'],
    ['Available', 'is_available'],
    ['Fixed Price', 'fixed_price'],
    ['Production Cost', 'production_cost'],
    ['Public Price', 'public_price'],
    ['Blueprints', 'blueprint_count'],
    ['Ordered', 'order_count'],
    [None, None], # hidden
]
@check_user_access()
def items(request):
    """
    Serves URL /industry/catalog/items/
    """
    columns = [ col[0] for col in COLUMNS ]
    return render_to_response('ecm/industry/catalog/items.html', {'columns' : columns}, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def items_data(request):
    """
    Serves URL /industry/catalog/items/data/ (jQuery datatables plugin)
    """
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.showUnavailable = REQ.get('showUnavailable', 'true') == 'true'
    except:
        return HttpResponseBadRequest()

    query = CatalogEntry.objects.all()
    query = query.annotate(blueprint_count=Count("blueprints"))
    query = query.annotate(order_count=Count("order_rows"))
    if not params.showUnavailable:
        query = query.filter(is_available=True)

    sort_col = COLUMNS[params.column][1]
    # SQL hack for making a case insensitive sort
    if params.column == 1:
        sort_col = sort_col + "_nocase"
        sort_val = db.fix_mysql_quotes('LOWER("%s")' % COLUMNS[params.column])
        query = query.extra(select={ sort_col : sort_val })

    if not params.asc:
        sort_col = "-" + sort_col
    query = query.extra(order_by=([sort_col]))

    if params.search:
        total_items = query.count()
        query = query.filter(typeName__icontains=params.search)
        filtered_items = query.count()
    else:
        total_items = filtered_items = query.count()

    items = []
    for item in query[params.first_id:params.last_id]:
        items.append([
            item.permalink,
            bool(item.is_available),
            print_float(item.fixed_price),
            print_float(item.production_cost),
            print_float(item.public_price),
            item.blueprint_count,
            item.order_count,
            item.typeID,
        ])

    return datatable_ajax_data(data=items, echo=params.sEcho,
                               total=total_items, filtered=filtered_items)

#------------------------------------------------------------------------------
@check_user_access()
def details(request, item_id):
    """
    Serves URL /industry/catalog/items/<item_id>/
    """
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()

    return render_to_response('ecm/industry/catalog/item_details.html', {'item': item}, Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def fixed_price(request, item_id):
    """
    Serves URL /industry/catalog/items/<item_id>/fixed_price/

    If request is GET:
        return the price as a raw float
    If request is POST:
        update the price of the item
        return the price formatted as a string
    """
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()
    if request.method == 'POST':
        try:
            price = float(request.POST['value'])
        except KeyError:
            return HttpResponseBadRequest('Missing "value" parameter')
        except ValueError:
            # price cannot be cast to a float
            price = None
        item.fixed_price = price
        item.save()
        displayPrice = print_float(price)
        logger.info('"%s" changed fixed_price for item "%s" -> %s' % (request.user,
                                                                     item.typeName,
                                                                     displayPrice))
        return HttpResponse(displayPrice)
    else:
        return HttpResponse(str(item.fixed_price or ''))

#------------------------------------------------------------------------------
@check_user_access()
def production_cost(request, item_id):
    """
    Serves URL /industry/catalog/items/<item_id>/production_cost/

    If request is GET:
        update the price of the item
        return the price formatted as a string
    """
    try:
        error = None
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
        try:
            update_production_cost(item, request.user)
        except Type.NoBlueprintException, err:
            # this can happen when blueprint requirements are not found in EVE database.
            # no way to work arround this issue for the moment, we just keep the price to None
            error = str(err)
        except OrderCannotBeFulfilled, err:
            if err.missing_prices:
                for supply in err.missing_prices:
                    Supply.objects.get_or_create(pk=supply)
            error = 'Cannot calculate production cost for "%s": %s' % (item.typeName, err)

        if error:
            return HttpResponseBadRequest(error)
        else:
            return HttpResponse(print_float(item.production_cost))

    except ValueError:
        raise Http404()

#------------------------------------------------------------------------------
@check_user_access()
def public_price(request, item_id):
    """
    Serves URL /industry/catalog/items/<item_id>/public_price/

    update the public price of the item
    return the price formatted as a string
    """
    try:
        error = None
        type_id = int(item_id)
        supply_source_id = Setting.get('industry_default_price_source')
        try:
            buyPrices = evecentral.get_buy_prices([type_id], supply_source_id)
            item = get_object_or_404(CatalogEntry, typeID=type_id)
            if buyPrices[type_id] > 0.0 and item.public_price != buyPrices[type_id]:
                item.public_price = buyPrices[type_id]
                logger.info('New price for "%s" -> %s' % (item.typeName,
                                                      print_float(buyPrices[type_id])))
                item.save()
        except KeyError:
            error = 'Could not find buy-price for item: "%s"' % item
            
        if error:
            return HttpResponseBadRequest(error)
        else:
            return HttpResponse(print_float(item.public_price))
    except ValueError:
        raise Http404()

#------------------------------------------------------------------------------
@check_user_access()
def availability(request, item_id):
    """
    Serves URL /industry/catalog/items/<item_id>/availability/

    If request is POST:
        update the availability of the item
    return the json formatted availability
    """
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()
    if request.method == 'POST':
        try:
            available = json.loads(request.POST['available'])
            if type(available) != type(True):
                return HttpResponseBadRequest('"available" parameter must be a boolean')
        except (KeyError, ValueError):
            return HttpResponseBadRequest('Missing "available" parameter')
        item.is_available = available
        item.save()
        logger.info('"%s" changed availability for item "%s" -> %s' % (request.user,
                                                                       item.typeName,
                                                                       available))
    return HttpResponse(json.dumps(item.is_available), mimetype=JSON)

#------------------------------------------------------------------------------
@check_user_access()
def add_blueprint(request, item_id):
    """
    Serves URL /industry/catalog/items/<item_id>/add_blueprint/

    Create a new blueprint for the given item.
    return the json formatted blueprint fields.
    """
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()
    bp = item.blueprints.create(typeID=item.blueprintTypeID)
    logger.info('"%s" created "%s" #%s' % (request.user, bp.typeName, bp.id))
    bp_dict = {
        'id': bp.id,
        'typeID': bp.typeID,
        'me': bp.me,
        'pe': bp.pe,
        'copy': bp.copy,
        'runs': bp.runs,
        'url': bp.url,
    }
    return HttpResponse(json.dumps(bp_dict), mimetype=JSON)
