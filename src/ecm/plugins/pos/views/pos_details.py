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
from ecm.views import extract_datatable_params
from ecm.apps.corp.models import Corp

__date__ = "2011-04-25"
__author__ = "JerryKhan"

import sys
import re
try:
    import json
except ImportError:
    import django.utils.simplejson as json

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponse, Http404, HttpResponseBadRequest

from ecm.plugins.pos.views import print_fuel_quantity, print_duration
from ecm.plugins.pos.models import POS, FuelConsumption, FuelLevel
from ecm.core.eve import db
from ecm.views.decorators import check_user_access
from ecm.plugins.pos import constants

COLUMNS = [
    ['Icon', 'typeID'],
    ['Name', 'typeID'],
    ['Quantity', 'quantity'],
    ['Burned Per Hour', None],
    ['Burned Per Day', None],
    ['Time Left', None],
]


MOON_REGEX = re.compile(".*\s+([^\s]+)\s+-\s+Moon\s+(\d+)")
#------------------------------------------------------------------------------
@check_user_access()
def onePos(request, pos_id):
    try:
        pos_id = int(pos_id)
    except ValueError:
        raise Http404()
    pos = get_object_or_404(POS, itemID=pos_id)

    match = MOON_REGEX.match(pos.moon)
    if match:
        dotlanPOSLocation = match.group(1) + '-Moon-' + match.group(2)
    else:
        dotlanPOSLocation = None

    try:
        corp = Corp.objects.latest()
        if pos.useStandingsFrom == corp.corporationID:
            useStandingsFrom = 'Corporation'
        elif pos.useStandingsFrom == corp.allianceID:
            useStandingsFrom = 'Alliance'
    except Corp.DoesNotExist:
        useStandingsFrom = "???"


    data = {
        'pos' : pos,
        'dotlanPOSLocation' : dotlanPOSLocation,
        'columns': [ col for col, _ in COLUMNS ],
        'useStandingsFrom': useStandingsFrom,
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

    pos = get_object_or_404(POS, itemID=pos_id)

    fuelTypeIDs = (
        constants.ENRICHED_URANIUM_TYPEID,
        constants.OXYGEN_TYPEID,
        constants.MECHANICAL_PARTS_TYPEID,
        constants.COOLANT_TYPEID,
        constants.ROBOTICS_TYPEID,
        constants.LIQUID_OZONE_TYPEID,
        constants.HEAVY_WATER_TYPEID,
        pos.isotopeTypeID,
        constants.STRONTIUM_CLATHRATES_TYPEID,
    )

    fuelTable = []
    for typeID in fuelTypeIDs:
        try:
            quantity = pos.fuel_levels.filter(typeID=typeID).latest().quantity
        except FuelLevel.DoesNotExist:
            quantity = 0
        try:
            fuelCons = pos.fuel_consumptions.get(typeID=typeID)
            if fuelCons.probableConsumption == 0:
                # if "probableConsumption" is 0, we fallback to "consumption"
                consumption = fuelCons.consumption
            else:
                consumption = fuelCons.probableConsumption
        except FuelConsumption.DoesNotExist:
            consumption = sys.maxint

        if consumption == 0:
            timeLeft = '-'
        else:
            hoursLeft = int(quantity / consumption)
            timeLeft = print_duration(hoursLeft)

        fuelTable.append([
            typeID,
            db.resolveTypeName(typeID)[0],
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
