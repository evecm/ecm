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
from django.contrib.auth.decorators import login_required

__date__ = "2012 2 2"
__author__ = "diabeteman"

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse,\
    HttpResponseNotFound

from ecm.core import JSON
from ecm.plugins.industry.models.catalog import CatalogEntry
from ecm.plugins.shop import eft

#------------------------------------------------------------------------------
@login_required
def parse_eft(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed()
    
    eft_block = request.POST.get('eft_block', None)
    if not eft_block:
        return HttpResponseBadRequest('Empty eft_block')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError, e:
        return HttpResponseBadRequest(str(e))
    
    items_dict = eft.parse_export(eft_block)
    query = CatalogEntry.objects.filter(typeName__in=items_dict.keys(), isAvailable=True)
    items = []
    for entry in query:
        items.append({
            'typeID': entry.typeID,
            'typeName': entry.typeName,
            'quantity': items_dict[entry.typeName] * quantity
        })
    return HttpResponse(json.dumps(items), mimetype=JSON)

#------------------------------------------------------------------------------
@login_required
def search_item(request):
    querystring = request.GET.get('q', None)
    try:
        limit = int(request.GET.get('limit', "10"))
    except ValueError:
        limit = 10
    if querystring is not None:
        query = CatalogEntry.objects.filter(typeName__icontains=querystring)
        query = query.filter(isAvailable=True).order_by('typeName')
        matches = query[:limit].values_list('typeName', flat=True)
        return HttpResponse( '\n'.join(matches) )
    else:
        return HttpResponseBadRequest()

#------------------------------------------------------------------------------
@login_required
def get_item_id(request):
    querystring = request.GET.get('q', None)
    if querystring is not None:
        query = CatalogEntry.objects.filter(typeName__iexact=querystring)
        if query.filter(isAvailable=True).exists():
            item = query[0]
            return HttpResponse( json.dumps( [item.typeID, item.typeName] ) )
        else:
            return HttpResponseNotFound()
    else:
        return HttpResponseBadRequest()
