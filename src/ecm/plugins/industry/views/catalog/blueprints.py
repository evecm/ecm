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


try:
    import json
except ImportError:
    # fallback for python 2.5
    import django.utils.simplejson as json
import logging

from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.template.context import RequestContext as Ctx
from django.shortcuts import get_object_or_404, render_to_response

from ecm.core.eve.classes import BpActivity
from ecm.plugins.industry.views import print_duration
from ecm.core import utils
from ecm.views import extract_datatable_params, datatable_ajax_data
from ecm.views.decorators import check_user_access
from ecm.plugins.industry.models.catalog import OwnedBlueprint

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
COLUMNS = [
    'Blueprint',
    'ME',
    'PE',
    'Copy',
    'Runs',
    None, # hidden
]
@check_user_access()
def blueprints(request):
    """
    Serves URL /industry/catalog/blueprints/
    """
    return render_to_response('catalog/blueprints.html', {'columns' : COLUMNS}, Ctx(request))
#------------------------------------------------------------------------------
@check_user_access()
def blueprints_data(request):
    """
    Serves URL /industry/catalog/blueprints/data/
    """
    try:
        params = extract_datatable_params(request)
        REQ = request.GET if request.method == 'GET' else request.POST
        params.displayMode = REQ.get('displayMode', 'all')
    except Exception, e:
        return HttpResponseBadRequest(str(e))

    query = list(OwnedBlueprint.objects.all())
    query.sort(key=lambda b: b.typeName)

    if params.displayMode == 'copies':
        query = [ bp for bp in query if bp.copy ]
    elif params.displayMode == 'originals':
        query = [ bp for bp in query if not bp.copy ]

    if params.search:
        total_items = len(query)
        query = [ bp for bp in query if params.search.lower() in bp.typeName.lower() ]
        filtered_items = len(query)
    else:
        total_items = filtered_items = len(query)

    blueprints = []
    for bp in query[params.first_id:params.last_id]:
        blueprints.append([
            bp.permalink,
            bp.me,
            bp.pe,
            bool(bp.copy),
            bp.runs,
            bp.id,
        ])

    return datatable_ajax_data(data=blueprints, echo=params.sEcho, 
                               total=total_items, filtered=filtered_items)
    

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

    activities = bp.activities.values()
    activities.sort(key=lambda a: a.activityID)
    data = {
        'blueprint': bp,
        'activities': activities,
        'prodDuration': print_duration(bp.getDuration(1, bp.pe, BpActivity.MANUFACTURING)),
        'meDuration': print_duration(bp.getDuration(1, bp.pe, BpActivity.RESEARCH_ME)),
        'peDuration': print_duration(bp.getDuration(1, bp.pe, BpActivity.RESEARCH_PE)),
        'copyDuration': print_duration(bp.getDuration(1, bp.pe, BpActivity.COPY)),
        'invDuration': print_duration(bp.getDuration(1, bp.pe, BpActivity.INVENTION)),
    }
    return render_to_response('catalog/blueprint_details.html', data, Ctx(request))

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
        REQ = request.GET if request.method == 'GET' else request.POST
        params.activityID = int(REQ.get('activityID', '1'))
    except (KeyError, ValueError), e:
        raise HttpResponseBadRequest(str(e))

    materials = bp.getBillOfMaterials(runs=1,
                                      meLevel=bp.me,
                                      activity=params.activityID,
                                      round_result=True)
    materials.sort(key=lambda m: m.typeID)

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
            utils.print_integer(mat.quantity),
            '%d%%' % (mat.damagePerJob * 100),
        ])

    return datatable_ajax_data(data=mat_table, echo=params.sEcho)
    
#------------------------------------------------------------------------------
@check_user_access()
def manufacturing_time(request, blueprint_id):
    """
    Serves URL /industry/catalog/blueprint/<blueprint_id>/time/
    """
    try:
        bp = get_object_or_404(OwnedBlueprint, id=int(blueprint_id))
    except (KeyError, ValueError), e:
        raise HttpResponseBadRequest(str(e))
    duration = print_duration(bp.getDuration(1, bp.pe, BpActivity.MANUFACTURING))
    return HttpResponse(duration)




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
