# Copyright (c) 2011 jerome Vacher
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

__date__ = "2011-04-25"
__author__ = "JerryKhan"

import re
try:
    import json
except ImportError:
    import django.utils.simplejson as json

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponse, Http404, HttpResponseBadRequest

from ecm.plugins.pos.views import print_fuel_quantity, print_duration
from ecm.plugins.pos.models import POS, FuelLevel
from ecm.core.eve import db
from ecm.views.decorators import check_user_access
from ecm.plugins.pos import constants
from ecm.views import extract_datatable_params
from ecm.apps.corp.models import Corp

COLUMNS = [
    ['Icon', 'type_id'],
    ['Name', 'type_id'],
    ['Quantity', 'quantity'],
    ['Burned Per Hour', None],
    ['Burned Per Day', None],
    ['Time Left', None],
]


MOON_REGEX = re.compile(".*\s+([^\s]+)\s+-\s+Moon\s+(\d+)")
#------------------------------------------------------------------------------
@check_user_access()
def one_pos(request, pos_id):
    try:
        pos_id = int(pos_id)
    except ValueError:
        raise Http404()
    pos = get_object_or_404(POS, item_id=pos_id)

    match = MOON_REGEX.match(pos.moon)
    if match:
        dotlanPOSLocation = match.group(1) + '-Moon-' + match.group(2)
    else:
        dotlanPOSLocation = None

    try:
        corp = Corp.objects.latest()
        if pos.use_standings_from == corp.corporationID:
            use_standings_from = 'Corporation'
        elif pos.use_standings_from == corp.allianceID:
            use_standings_from = 'Alliance'
        else:
            use_standings_from = pos.use_standings_from
    except Corp.DoesNotExist:
        use_standings_from = "???"


    data = {
        'pos' : pos,
        'dotlanPOSLocation' : dotlanPOSLocation,
        'columns': [ col for col, _ in COLUMNS ],
        'use_standings_from': use_standings_from,
    }
    return render_to_response("pos_details.html", data, RequestContext(request))

#------------------------------------------------------------------------------
@check_user_access()
def fuel_data(request, pos_id):
    try:
        params = extract_datatable_params(request)
        pos_id = int(pos_id)
    except:
        return HttpResponseBadRequest()

    pos = get_object_or_404(POS, item_id=pos_id)

    fuelTypeIDs = (
        pos.fuel_type_id,
        constants.STRONTIUM_CLATHRATES_TYPEID,
    )

    fuelTable = []
    for type_id in fuelTypeIDs:
        try:
            fuel = pos.fuel_levels.filter(type_id=type_id).latest()
            quantity = fuel.quantity
            consumption = fuel.consumption
        except FuelLevel.DoesNotExist:
            quantity = 0
            consumption = 0
        if consumption == 0:
            timeLeft = '-'
        else:
            hoursLeft = int(quantity / consumption)
            timeLeft = print_duration(hoursLeft)

        fuelTable.append([
            type_id,
            db.get_type_name(type_id)[0],
            print_fuel_quantity(quantity),
            '%d / hour' % consumption,
            '%d / day' % (consumption * 24),
            timeLeft,
        ])



    json_data = {
        "sEcho" : params.sEcho,
        "iTotalRecords" : len(fuelTypeIDs),
        "iTotalDisplayRecords" : len(fuelTypeIDs),
        "aaData" : fuelTable
    }
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
def update_pos_name(request, pos_id):
    try:
        new_name = request.POST["value"]
        pos = get_object_or_404(POS, item_id=int(pos_id))
        pos.custom_name = new_name
        pos.save()

        return HttpResponse(new_name)
    except:
        return HttpResponseBadRequest()
