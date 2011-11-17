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
from ecm.core.eve.classes import Blueprint, BpActivity

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
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect

from ecm.core import utils
from ecm.views import extract_datatable_params
from ecm.views.decorators import check_user_access
from ecm.plugins.industry.models.catalog import CatalogEntry, OwnedBlueprint

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@check_user_access()
def all(request):
    """
    Serves URL /industry/catalog/blueprints/
    """
    return render_to_response('catalog/blueprints.html', {}, RequestContext(request))
#------------------------------------------------------------------------------
@check_user_access()
def all_data(request):
    """
    Serves URL /industry/catalog/blueprints/data/
    """
    return HttpResponse()

#------------------------------------------------------------------------------
@check_user_access()
def details(request, blueprint_id):
    """
    Serves URL /industry/catalog/blueprints/<blueprint_id>/
    """
    try:
        bp = get_object_or_404(OwnedBlueprint, id=int(blueprint_id))
    except ValueError:
        raise Http404()
    data = {
        'blueprint': bp,
    }
    return render_to_response('catalog/blueprint_details.html', data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
def materials(request, blueprint_id):
    """
    Serves URL /industry/catalog/blueprints/<blueprint_id>/materials/
    (jQuery datatables)
    """
    try:
        bp = get_object_or_404(OwnedBlueprint, id=int(blueprint_id))
        params = extract_datatable_params(request)
    except (KeyError, ValueError), e:
        raise HttpResponseBadRequest(str(e))

    materials = bp.getBillOfMaterials(runs=1,
                                      meLevel=bp.me,
                                      activity=BpActivity.MANUFACTURING,
                                      round_result=True)
    mat_table = []
    for mat in materials:
        if mat.blueprintTypeID is not None:
            url = '/industry/catalog/items/%d/' % mat.typeID
            css = 'catalog-item'
        else:
            url = '/industry/catalog/supplies/%d/' % mat.typeID
            css = 'catalog-supply'
        mat_table.append([
            mat.typeID,
            '<a href="%s" class="%s">%s</a>' % (url, css, mat.typeName),
            mat.quantity,
            "{:.00%}".format(mat.damagePerJob),
        ])

    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : len(mat_table),
        "iTotalDisplayRecords" : len(mat_table),
        "aaData" : mat_table
    }
    return HttpResponse(json.dumps(json_data))



#------------------------------------------------------------------------------
@check_user_access()
def delete(request, blueprint_id):
    """
    Serves URL /industry/catalog/blueprints/<blueprint_id>/delete/
    """
    try:
        blueprint_id = int(blueprint_id)
        bp = get_object_or_404(OwnedBlueprint, id=blueprint_id)
    except ValueError:
        raise Http404()
    bp.delete()
    logger.info('"%s" deleted "%s" #%s' % (request.user, bp.typeName, blueprint_id))
    return HttpResponse()

#------------------------------------------------------------------------------
@check_user_access()
def info(request, attr):
    """
    Serves URL /industry/catalog/blueprints/<attr>/

    must have "id" and "value" parameters in the request
    if request is POST:
        update bp.attr with value
    return the bp.attr as JSON
    """
    try:
        blueprint_id = getattr(request, request.method)['id']
        bp = get_object_or_404(OwnedBlueprint, id=int(blueprint_id))
        if not hasattr(bp, attr):
            # unknown attribute
            raise Http404()
    except KeyError:
        return HttpResponseBadRequest('Missing "id" parameter')
    except ValueError:
        raise Http404()

    if request.method == 'POST':
        try:
            value = json.loads(request.POST['value'])
            if type(value) == type(getattr(bp, attr)):
                setattr(bp, attr, value)
                bp.save()
                logger.info('"%s" changed "%s" #%d (%s -> %s)' % (request.user, bp.typeName,
                                                                  bp.id, attr, value))
        except KeyError:
            return HttpResponseBadRequest('Missing "value" parameter')
        except ValueError:
            return HttpResponseBadRequest('Cannot parse "value" parameter')

    return HttpResponse(json.dumps(getattr(bp, attr)))
