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

try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponse,\
    HttpResponseNotFound

from ecm.core import JSON
from ecm.plugins.industry.models.catalog import CatalogEntry
from ecm.plugins.shop import eft
from ecm.apps.common.models import Setting

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
    
    member_group_name = Setting.get('hr_corp_members_group_name')
    if request.user.groups.filter(name=member_group_name):
        margin = Setting.get('industry_internal_price_margin')
    else:
        margin = Setting.get('industry_external_price_margin')
    
    query = CatalogEntry.objects.filter(typeName__in=items_dict.keys(), is_available=True)
    items = []
    for entry in query:
        price = entry.fixed_price or entry.production_cost
        if price is not None:
            price *= 1 + margin
        items.append({
            'typeID': entry.typeID,
            'typeName': entry.typeName,
            'quantity': items_dict[entry.typeName] * quantity,
            'price': price
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
        query = query.filter(is_available=True).order_by('typeName')
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
        if query.filter(is_available=True).exists():
            item = query[0]
            price = item.fixed_price or item.production_cost
            
            member_group_name = Setting.get('hr_corp_members_group_name')
            if request.user.groups.filter(name=member_group_name):
                margin = Setting.get('industry_internal_price_margin')
            else:
                margin = Setting.get('industry_external_price_margin')
            
            if price is not None:
                price *= 1 + margin
            return HttpResponse( json.dumps( [item.typeID, item.typeName, price] ) )
        else:
            return HttpResponseNotFound()
    else:
        return HttpResponseBadRequest()
