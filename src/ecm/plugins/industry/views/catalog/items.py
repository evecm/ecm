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

__date__ = "2011 11 13"
__author__ = "diabeteman"


try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json
import logging

from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.template.context import RequestContext
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render_to_response

from ecm.core import utils
from ecm.views import extract_datatable_params
from ecm.views.decorators import check_user_access
from ecm.plugins.industry.models.catalog import CatalogEntry

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
COLUMNS = [
    ['Item', 'typeName'],
    ['Available', 'isAvailable'],
    ['Fixed Price', 'fixedPrice'],
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
    return render_to_response('catalog/items.html', {'columns' : columns}, RequestContext(request))

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
        query = query.filter(isAvailable=True)

    sort_col = COLUMNS[params.column][1]
    # SQL hack for making a case insensitive sort
    if params.column == 1:
        sort_col = sort_col + "_nocase"
        sort_val = utils.fix_mysql_quotes('LOWER("%s")' % COLUMNS[params.column])
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
            bool(item.isAvailable),
            utils.print_float(item.fixedPrice),
            item.blueprint_count,
            item.order_count,
            item.typeID,
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : total_items,
        "iTotalDisplayRecords" : filtered_items,
        "aaData" : items
    }
    return HttpResponse(json.dumps(json_data))

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

    return render_to_response('catalog/item_details.html', {'item': item}, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
def price(request, item_id):
    """
    Serves URL /industry/catalog/items/<item_id>/price/
    
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
            price = float(request.POST['price'])
        except KeyError:
            return HttpResponseBadRequest('Missing "price" parameter')
        except ValueError:
            # price cannot be cast to a float
            price = None
        item.fixedPrice = price
        item.save()
        displayPrice = utils.print_float(price)
        logger.info('"%s" changed fixedPrice for item "%s" -> %s' % (request.user, 
                                                                     item.typeName, 
                                                                     displayPrice))
        return HttpResponse(displayPrice)
    else:
        return HttpResponse(str(item.fixedPrice))

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
        item.isAvailable = available
        item.save()
        logger.info('"%s" changed availability for item "%s" -> %s' % (request.user, 
                                                                       item.typeName, 
                                                                       available))
    return HttpResponse(json.dumps(item.isAvailable))

#------------------------------------------------------------------------------
@check_user_access()
def blueprint_add(request, item_id):
    """
    Serves URL /industry/catalog/items/<item_id>/addblueprint/
    
    Create a new blueprint for the given item.
    return the json formatted blueprint fields.
    """
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()
    bp = item.blueprints.create(blueprintTypeID=item.blueprintTypeID)
    logger.info('"%s" created "%s" #%s' % (request.user, bp.typeName, bp.id))
    bp_dict = {
                     'id': bp.id, 
        'blueprintTypeID': item.blueprintTypeID, 
                     'me': bp.me, 
                     'pe': bp.pe, 
                   'copy': bp.copy, 
                   'runs': bp.runs, 
                    'url': bp.url,
    }
    return HttpResponse(json.dumps(bp_dict))
