'''
Created on 12 Mar 2012

@author: Ajurna
'''
__author__ = "Ajurna"

try:
    import json
except ImportError:
    import django.utils.simplejson as json
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.plugins.industry.models import OwnedBlueprint, CatalogEntry
from ecm.apps.eve.models import Type, CelestialObject
from ecm.plugins.assets.models import Asset
from ecm.views import extract_datatable_params
from ecm.views.decorators import check_user_access

COLUMNS = [
          ['#'        , 'id'],
          ['Name'     , 'name'],
          ['Location' , 'location'],
          ['Original' , 'is_original'],
          ['Import'   , 'import'],
]
FILTER_TYPES = {'0' : 'BPO',
                '1' : 'BPC'}

BLUEPRINTS_CATEGORYID = 9

#------------------------------------------------------------------------------
@check_user_access()
def list_bps(request):
    columns = [ col[0] for col in COLUMNS ]
    
    return render_to_response('catalog/addbp.html',
                              {'columns' : columns,
                               'filter'  : FILTER_TYPES},
                              Ctx(request))

#------------------------------------------------------------------------------
@check_user_access()
def get_bps(request):
    #pull page params
    try:
        params = extract_datatable_params(request)
    except Exception, e:
        return HttpResponseBadRequest(str(e))
    total_count = Asset.objects.exclude(is_original=None).count()
    #gather the initial list by filter type (bpo or bpc)
    filters = []
    try:
        filters_list = [int(x) for x in request.GET.get('filter').split(',')]
        if 1 in filters_list:
            filters.append(False)
        if 0 in filters_list:
            filters.append(True)
    except ValueError:
        filters.append(None)
    #generate list with search based items
    if params.search:
        matchingids = [item.typeID for item in Type.objects.filter(typeName__contains = params.search)]
        query = Asset.objects.filter(typeID__in          = matchingids, 
                                     is_original__isnull = False,
                                     is_original__in     = filters)
    else:
        query = Asset.objects.filter(is_original__in = filters)
    #remove non search based items.
    owned_prints = [(item.typeID, item.is_original) for item in OwnedBlueprint.objects.all()]
    without_owned = query
    for bp in query:
        if (bp.typeID, bp.is_original) in owned_prints:
            owned_prints.remove((bp.typeID, bp.is_original))
            without_owned = without_owned.exclude(itemID = bp.itemID)
    #finish filtered list and prep it for display.
    filtered_count = without_owned.count()
    prints = []
    for bp in without_owned[params.first_id:params.last_id]:
        try:
            location_name = CelestialObject.objects.get(itemID = bp.stationID).itemName
        except CelestialObject.DoesNotExist:
            location_name = CelestialObject.objects.get(itemID = bp.closest_object_id).itemName
        prints.append([bp.itemID,
                       bp.typeName,
                       location_name,
                       bp.is_original,
                       False])
    json_data = {
        "sEcho"                : params.sEcho,
        "iTotalRecords"        : total_count,  # Number of lines
        "iTotalDisplayRecords" : filtered_count,# Number of displayed lines,
        "aaData"               : prints
    }
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
def add_bps(request):
    bp_list = []
    for item in request.POST:
        if request.POST[item] == 'on':
            bp_list.append(item)
    bp_list = Asset.objects.filter(itemID__in = bp_list)
    for bp in bp_list:
        try:
            catalog_entry = CatalogEntry.objects.get(typeID = bp.typeID)
        except CatalogEntry.DoesNotExist:
            catalog_entry = CatalogEntry(typeID = bp.typeID,
                                         typeName = bp.typeName,
                                         is_available = False)
            catalog_entry.save()
        newbp = OwnedBlueprint(typeID = bp.typeID,
                               me = 0,
                               pe = 0,
                               copy = (not bp.is_original),
                               runs = 0,
                               catalog_entry = catalog_entry)
        newbp.save()
    return HttpResponseRedirect('/industry/catalog/addbp/')





