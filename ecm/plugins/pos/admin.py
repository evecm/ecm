# Copyright (c) 2010-2011 Jerome Vacher
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

__date__ = "2011 04 23"
__author__ = "JerryKhan"

from django.contrib import admin

from ecm.plugins.pos.models import POS, FuelLevel

#------------------------------------------------------------------------------
class POSAdmin(admin.ModelAdmin):
    list_display = ['moon',
                    'type_name',
                    'state',
                    'online_timestamp',
                    'cached_until',
                    'isotopes_admin_display']

#------------------------------------------------------------------------------
class FuelLevelAdmin(admin.ModelAdmin):
    list_display = ['pos',
                    'date',
                    'fuel_admin_display',
                    'quantity']

#------------------------------------------------------------------------------
admin.site.register(POS, POSAdmin)
admin.site.register(FuelLevel, FuelLevelAdmin)
