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

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from django.http import HttpResponse, Http404, HttpResponseBadRequest, HttpResponseRedirect

from ecm.utils import _json as json
from ecm.utils.format import print_duration
from ecm.plugins.pos.views import print_fuel_quantity
from ecm.plugins.pos.models import POS, FuelLevel
from ecm.apps.eve.models import Type
from ecm.views.decorators import check_user_access
from ecm.plugins.assets.models import Asset
from ecm.plugins.pos import constants
from ecm.views import extract_datatable_params
from ecm.apps.corp.models import Corporation
from ecm.apps.common.models import UrlPermission, Setting
from django.contrib.auth.models import User

FUEL_COLUMNS = [
    ['Icon',            'type_id'],
    ['Name',            'type_id'],
    ['Quantity',        'quantity'],
    ['Burned Per Hour', None],
    ['Burned Per Day',  None],
    ['Time Left',       None],
]

SILO_COLUMNS = [
    ['Icon',                    'type_id'],
    ['Name',                    'type_id'],
    ['Quantity',                'quantity'],
    ['Time Left until full',    None],
]
OPERATOR_COLUMNS = [
    ['Username',    'username'],
    ['Characters',  'chars'],
    ['Titles',      'titles'],
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
    #check if superuser
    if not request.user.is_superuser:
        #check if there are authorised groups
        if not len(pos.authorized_groups.all()) == 0:
            #check if user in authorised group!
            if len(set(request.user.groups.all()) & set(pos.authorized_groups.all())) == 0:
                raise Http404()
    match = MOON_REGEX.match(pos.moon)
    if match:
        dotlanPOSLocation = match.group(1) + '-Moon-' + match.group(2)
    else:
        dotlanPOSLocation = None

    try:
        corp = Corporation.objects.mine()
        try:
            allianceid = corp.alliance.allianceID
        except AttributeError:
            allianceid = 0
        if pos.use_standings_from == corp.corporationID:
            use_standings_from = 'Corporation'
        elif pos.use_standings_from == allianceid:
            use_standings_from = 'Alliance'
        else:
            use_standings_from = pos.use_standings_from
    except Corporation.DoesNotExist:
        use_standings_from = "???"

    groups = UrlPermission.objects.get(pattern='^/pos/.*$').groups.all()
    operators = User.objects.filter(groups__in=groups).distinct().extra(select={ 'lower_name': 'lower(username)' })

    data = {
        'pos'               : pos,
        'moon'              : pos.moon_id,
        'system'            : pos.location_id,
        'opers'             : operators.order_by('lower_name'),
        'dotlanPOSLocation' : dotlanPOSLocation,
        'fuel_columns'      : [ col for col, _ in FUEL_COLUMNS ],
        'silo_columns'      : [ col for col, _ in SILO_COLUMNS ],
        'oper_columns'      : [ col for col, _ in OPERATOR_COLUMNS],
        'use_standings_from': use_standings_from,
    }
    return render_to_response("ecm/pos/pos_details.html", data, RequestContext(request))

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
            quantity = fuel.current_fuel()
            consumption = fuel.consumption
        except FuelLevel.DoesNotExist:
            quantity = 0
            consumption = 0
        if consumption == 0:
            timeLeft = '-'
        else:
            hoursLeft = int(quantity / consumption)
            timeLeft = print_duration(seconds=hoursLeft * 3600, verbose=False)

        fuelTable.append([
            type_id,
            Type.objects.get(typeID=type_id).typeName,
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
def silo_data(request, pos_id):
    try:
        params = extract_datatable_params(request)
        pos_id = int(pos_id)
    except:
        return HttpResponseBadRequest()
    pos = get_object_or_404(POS, item_id=pos_id)
    #silo's are actually the moon mins. this is just the quickest way
    #using the Assets table. might make this work properly at some point.
    silos = Asset.objects.filter(closest_object_id = pos.moon_id,
                                 flag = constants.SILO_TYPEID)
    silo_table = []
    for silo in silos:
        mineral = Type.objects.get(typeID = silo.eve_type_id)
        if pos.fuel_type_id == constants.GALLENTE_FUEL_BLOCK_TYPEID:
            remaining_vol = (constants.SILO_VOLUME * 2.0) - silo.volume
            remaining_per = int((1.0 * silo.volume / (constants.SILO_VOLUME * 2.0)) * 100)
        elif pos.fuel_type_id == constants.AMARR_FUEL_BLOCK_TYPEID:
            remaining_vol = (constants.SILO_VOLUME * 1.5) - silo.volume
            remaining_per = int((1.0 * silo.volume / (constants.SILO_VOLUME * 1.5)) * 100)
        else:
            remaining_vol = constants.SILO_VOLUME - silo.volume
            remaining_per = int((1.0 * silo.volume / (constants.SILO_VOLUME)) * 100)
        if mineral.typeID in constants.COMPLEX_REACTIONS:
            hours_to_full = remaining_vol / (mineral.volume * constants.COMPLEX_REACTIONS[mineral.typeID])
        elif mineral.typeID in constants.SIMPLE_REACTIONS:
            hours_to_full = remaining_vol / (mineral.volume * 200)
        elif mineral.typeID in constants.UNREFINED:
            hours_to_full = remaining_vol / (mineral.volume * 1)
        else:
            hours_to_full = remaining_vol / (mineral.volume * 100)

        silo_div = '<div class="progress"><div class="bar" style="width: '
        silo_div += str(remaining_per)+'%;"><span style="color:black;">'
        silo_div += print_duration(seconds=hours_to_full * 3600, verbose=False)
        silo_div += '</span></div></div>'
        silo_table.append([
            silo.eve_type_id,
            mineral.typeName,
            silo.quantity,
            silo_div,
            #print_duration(seconds=hours_to_full * 3600, verbose=False)
        ])
    silo_count = silos.count()
    json_data = {
        "sEcho"                 : params.sEcho,
        "iTotalRecords"         : silo_count,
        "iTotalDisplayRecords"  : silo_count,
        "aaData"                : silo_table,
    }
    return HttpResponse(json.dumps(json_data))

#------------------------------------------------------------------------------
@check_user_access()
def oper_data(request, pos_id):
    try:
        params = extract_datatable_params(request)
        pos_id = int(pos_id)
    except:
        return HttpResponseBadRequest()
    pos = get_object_or_404(POS, item_id=pos_id)
    oper_table = []
    members = Setting.get('hr_corp_members_group_name')
    for user in pos.operators.all():
        oper_table.append([
            user.username,
            ', '.join(user.characters.all().values_list('name', flat=True)),
            ', '.join(user.groups.exclude(name=members).values_list('name', flat=True)),
        ])
        
    operator_count = pos.operators.all().count()
    json_data = {
        "sEcho"                 : params.sEcho,
        "iTotalRecords"         : operator_count,
        "iTotalDisplayRecords"  : operator_count,
        "aaData"                : oper_table,
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

#------------------------------------------------------------------------------
@check_user_access()
def update_pos_oper(request, pos_id):
    user_id = request.POST["user"]
    try:
        pos = get_object_or_404(POS, item_id=int(pos_id))
        user = get_object_or_404(User, id=int(user_id))
    except ValueError:
        return HttpResponseRedirect('/pos/' + pos_id + '/')
    if user in pos.operators.all():
        pos.operators.remove(user)
    else:
        pos.operators.add(user)
    pos.save()
    return HttpResponseRedirect('/pos/' + pos_id + '/')


