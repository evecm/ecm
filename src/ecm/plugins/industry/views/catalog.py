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
from django.db.models.aggregates import Count

__date__ = "2011 11 13"
__author__ = "diabeteman"


try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect

from ecm.core import utils
from ecm.views import extract_datatable_params
from ecm.views.decorators import check_user_access
from ecm.plugins.industry.models.catalog import CatalogEntry


#------------------------------------------------------------------------------
COLUMNS = [
    ['Item', 'typeName'],
    ['Available', 'isAvailable'],
    ['Blueprints', 'blueprint_count'],
    ['Ordered', 'order_count'],
    [None, None], # hidden
]
@check_user_access()
def catalog(request):
    try:
        if request.method == 'POST':
            available = request.POST.get('available', '')
            unavailable = request.POST.get('unavailable', '')
            if available:
                available = [ int(typeID.strip()) for typeID in available.split(',') ]
                CatalogEntry.objects.filter(typeID__in=available).update(isAvailable=True)
            if unavailable:
                unavailable = [ int(typeID.strip()) for typeID in unavailable.split(',') ]
                CatalogEntry.objects.filter(typeID__in=unavailable).update(isAvailable=False)
    except ValueError, e:
        pass

    columns = [ col[0] for col in COLUMNS ]
    return render_to_response('catalog.html', {'columns' : columns}, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
def catalog_data(request):
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
def item_details(request, item_id):
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()

    return render_to_response('catalog_details.html', {'item': item}, RequestContext(request))


#------------------------------------------------------------------------------
@check_user_access()
def add_blueprint(request, item_id):
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()

    copy = request.POST.get('copy', 'off') == 'on'
    me = int(request.POST.get('me', '0'))
    pe = int(request.POST.get('pe', '0'))
    runs = int(request.POST.get('runs', '0'))

    item.blueprints.create(blueprintTypeID=item.blueprintTypeID,
                           copy=copy,
                           me=me,
                           pe=pe,
                           runs=runs)

    return redirect('/industry/catalog/%s/' % item_id)


#------------------------------------------------------------------------------
@check_user_access()
def get_price(request, item_id):
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()
    return HttpResponse(str(item.fixedPrice))

#------------------------------------------------------------------------------
@check_user_access()
def update_price(request, item_id):
    try:
        item = get_object_or_404(CatalogEntry, typeID=int(item_id))
    except ValueError:
        raise Http404()
    price = request.POST.get('value', '')
    try:
        price = float(price)
    except ValueError:
        price = None

    item.fixedPrice = price
    item.save()

    return utils.print_float(price)
