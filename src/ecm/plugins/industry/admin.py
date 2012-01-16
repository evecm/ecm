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

__date__ = "2011 6 9"
__author__ = "diabeteman"

from django.contrib import admin

from ecm.plugins.industry.models import InventionPolicy, Job, Order, \
                                     OrderLog, OrderRow, OwnedBlueprint, PriceHistory, \
                                     Pricing, SupplySource, \
                                     Supply, CatalogEntry

#------------------------------------------------------------------------------
class MileStoneAdmin(admin.ModelAdmin):
    list_display = ['date']

#------------------------------------------------------------------------------
class PricingAdmin(admin.ModelAdmin):
    list_display = ['name', 'margin_admin_display']

#------------------------------------------------------------------------------
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "originator",
        "manufacturer",
        "deliveryMan",
        "client",
        "deliveryLocation",
        "deliveryDate",
        "state",
        "pricing",
        "extraDiscount",
        "quote",
    ]

#------------------------------------------------------------------------------
class OrderLogAdmin(admin.ModelAdmin):
    list_display = ["order", "state", "date", "user", "text" ]

#------------------------------------------------------------------------------
class OrderRowAdmin(admin.ModelAdmin):
    list_display = ["catalogEntry", "quantity", "cost", "order", ]

#------------------------------------------------------------------------------
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "row",
        "parentJob",
        "state",
        "owner",
        "itemID",
        "runs",
        "blueprint",
        "activity",
        "duration",
        "startDate",
        "endDate",
    ]
#------------------------------------------------------------------------------
class SupplySourceAdmin(admin.ModelAdmin):
    list_display = ["name", "locationID"]

#------------------------------------------------------------------------------
class SupplyAdmin(admin.ModelAdmin):
    list_display = ["item_admin_display", "price", "autoUpdate", "supplySource"]

#------------------------------------------------------------------------------
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ["item_admin_display", "price", "date"]

#------------------------------------------------------------------------------
class CatalogEntryAdmin(admin.ModelAdmin):
    list_display = [
        "typeName",
        "typeID",
        "marketGroupID",
        "fixedPrice",
        "isAvailable",
    ]

#------------------------------------------------------------------------------
class OwnedBlueprintAdmin(admin.ModelAdmin):
    list_display = [
        "item_name_admin_display",
        "blueprintTypeID",
        "me",
        "pe",
        "copy",
        "runs",
    ]
#------------------------------------------------------------------------------
class InventionPolicyAdmin(admin.ModelAdmin):
    list_display = [
        "itemGroupName",
        "itemGroupID",
        "invention_chance_admin_display",
        "targetME",
    ]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLog, OrderLogAdmin)
admin.site.register(OrderRow, OrderRowAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(Pricing, PricingAdmin)
admin.site.register(SupplySource, SupplySourceAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(PriceHistory, PriceHistoryAdmin)
admin.site.register(CatalogEntry, CatalogEntryAdmin)
admin.site.register(OwnedBlueprint, OwnedBlueprintAdmin)
admin.site.register(InventionPolicy, InventionPolicyAdmin)

