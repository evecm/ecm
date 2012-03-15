# Copyright (c) 2010-2012 Robin Jarry, Ajurna
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
from django.db import transaction

__author__ = 'Ajurna'
__author__ = '12 Mar 2012'

from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.plugins.industry.models import OwnedBlueprint, CatalogEntry
from ecm.apps.eve.models import Type, CelestialObject
from ecm.plugins.assets.models import Asset
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.views.decorators import check_user_access

COLUMNS = [
          ['#'        , 'id'],
          ['Name'     , 'name'],
          ['Location' , 'location'],
          ['Original' , 'is_original'],
]

BLUEPRINTS_CATEGORYID = 9

#------------------------------------------------------------------------------
@transaction.commit_on_success
@check_user_access()
def blueprints(request):
    error = None
    imported = 0
    if request.method == 'POST':
        try:
            blueprint_ids = request.POST.get('blueprints', '')
            if not blueprint_ids:
                raise ValueError('No blueprint selected.')
            elif blueprint_ids == 'all':
                bps_to_import = get_missing_blueprints()
            else:
                blueprint_ids = [ int(bp) for bp in blueprint_ids.split(',') ]
                bps_to_import = Asset.objects.filter(itemID__in=blueprint_ids)

            imported = bps_to_import.count()
            for bp in bps_to_import:
                catalog_entry, _ = CatalogEntry.objects.get_or_create(typeID=bp.typeID,
                                                                      typeName=bp.typeName,
                                                                      is_available=False)
                catalog_entry.blueprints.create(typeID=bp.typeID)
        except ValueError, err:
            error = err

    columns = [ col[0] for col in COLUMNS ]
    data = {
        'columns' : columns,
        'error': error,
        'imported': imported,
    }
    return render_to_response('catalog/import_blueprints.html', data, Ctx(request))


#------------------------------------------------------------------------------
@check_user_access()
def blueprints_data(request):

    # FIXME: this function locks the interpreter when all BPOs are already imported


    # pull request params
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.displayMode = REQ.get('displayMode', 'originals')
    except Exception, e:
        return HttpResponseBadRequest(str(e))


    query = get_missing_blueprints(only_originals=False)

    total_count = query.count()

    if params.displayMode == 'copies':
        query = query.filter(is_bpc=True)
    elif params.displayMode == 'originals':
        query = query.filter(is_bpc=False)

    # handle search string
    if params.search:
        matching_items = Type.objects.filter(typeName__icontains=params.search)
        matching_ids = matching_items.values_list('typeID', flat=True)
        query = query.filter(typeID__in=matching_ids)

    filtered_count = query.count()

    # finish filtered list and prep it for display.
    prints = []
    for bp in query[params.first_id:params.last_id]:
        try:
            location_name = CelestialObject.objects.get(itemID=bp.stationID).itemName
        except CelestialObject.DoesNotExist:
            location_name = CelestialObject.objects.get(itemID=bp.closest_object_id).itemName

        prints.append([
           bp.itemID,
           bp.typeName,
           location_name,
           not bp.is_bpc,
        ])

    return datatable_ajax_data(data=prints, echo=params.sEcho,
                               total=total_count, filtered=filtered_count)

#------------------------------------------------------------------------------
def get_missing_blueprints(only_originals=True):
    assets_qry = Asset.objects.filter(is_bpc__isnull=False)
    if only_originals:
        assets_qry = assets_qry.filter(is_bpc=False)

    # remove already imported blueprints
    already_imported = [(bp.typeID, bp.copy) for bp in OwnedBlueprint.objects.all()]
    query = assets_qry
    for asset in assets_qry:
        if (asset.typeID, asset.is_bpc) in already_imported:
            already_imported.remove((asset.typeID, asset.is_bpc))
            query = query.exclude(itemID=asset.itemID)

    return query