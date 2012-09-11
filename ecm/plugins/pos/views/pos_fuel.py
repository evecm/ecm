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

__date__ = "2012 06 29"
__author__ = "Ajurna"


from django.shortcuts import render_to_response
from django.template.context import RequestContext

from ecm.plugins.pos.models import POS, FuelLevel
from ecm.apps.eve.models import Type
from ecm.views.decorators import check_user_access

@check_user_access()
def pos_fuel(request):
    pos_list = POS.objects.all()
    fuels = {}
    for pos in pos_list:
        try:
            fuel = pos.fuel_levels.filter(type_id = pos.fuel_type_id).latest()
            fuel_name = Type.objects.get(typeID = pos.fuel_type_id)
            if fuels.has_key(fuel_name.typeName):
                fuels[fuel_name.typeName] += fuel.consumption
            else:
                fuels[fuel_name.typeName] = fuel.consumption
        except FuelLevel.DoesNotExist:
            pass
    for fuel in fuels:
        counts = []
        counts.append(fuels[fuel])
        counts.append(fuels[fuel] * 24)     #day
        counts.append(fuels[fuel] * 168)    #week
        counts.append(fuels[fuel] * 336)    #two weeks
        counts.append(fuels[fuel] * 672)    #28 days
        fuels[fuel] = counts
    data = {
           'fuels' : fuels
           }
    return render_to_response("ecm/pos/pos_fuel.html", data, RequestContext(request))
