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
#from ecm.plugins.industry.models.catalog import PricingPolicy

__date__ = '2011 6 9'
__author__ = 'diabeteman'

from django.contrib import admin

from ecm.plugins.industry.models import *

#------------------------------------------------------------------------------
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'originator',
        'responsible',
        'delivery_boy',
        'client',
        'delivery_location',
        'delivery_date',
        'state',
        'quote',
    ]
    search_fields = ['originator__username', 'client', 'responsible__username',
                     'delivery_boy__username', 'delivery_location']

#------------------------------------------------------------------------------
class OrderLogAdmin(admin.ModelAdmin):
    list_display = ['order', 'state', 'date', 'user', 'text' ]
    search_fields = ['user__username', 'text']

#------------------------------------------------------------------------------
class OrderRowAdmin(admin.ModelAdmin):
    list_display = ['catalog_entry', 'quantity', 'cost', 'order', ]
    search_fields = ['catalog_entry__typeName']

#------------------------------------------------------------------------------
class JobAdmin(admin.ModelAdmin):
    list_display = [
        'order',
        'row',
        'parent_job',
        'state',
        'assignee',
        'item_id',
        'runs',
        'blueprint',
        'activity',
        'duration',
        'start_date',
        'end_date',
    ]
#------------------------------------------------------------------------------
class SupplySourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'location_id']

#------------------------------------------------------------------------------
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['item_admin_display', 'price', 'auto_update', 'supply_source']
    search_fields = ['item_admin_display']    

#------------------------------------------------------------------------------
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['item_admin_display', 'price', 'date']

#------------------------------------------------------------------------------
class CatalogEntryAdmin(admin.ModelAdmin):
    list_display = [
        'typeName',
        'typeID',
        'production_cost',
        'public_price',
        'last_update',
        'fixed_price',
        'is_available',
    ]

#------------------------------------------------------------------------------
class OwnedBlueprintAdmin(admin.ModelAdmin):
    list_display = [
        'item_name_admin_display',
        'typeID',
        'me',
        'pe',
        'copy',
        'runs',
    ]
#------------------------------------------------------------------------------
class InventionPolicyAdmin(admin.ModelAdmin):
    list_display = [
        'item_group',
        'item_group_id',
        'item_id',
        'skills_admin_display',
        'me_mod',
        'chance_mod_admin_display'
    ]
#------------------------------------------------------------------------------
class PricingPolicyAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'is_active',
        'item_group',
        'user_group',
        'surcharge_relative_admin_display',
        'surcharge_absolute_admin_display',
        'priority',
    ]

#------------------------------------------------------------------------------
class ItemGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'item_count']
    filter_horizontal = ['items']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderLog, OrderLogAdmin)
admin.site.register(OrderRow, OrderRowAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(SupplySource, SupplySourceAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(PriceHistory, PriceHistoryAdmin)
admin.site.register(CatalogEntry, CatalogEntryAdmin)
admin.site.register(OwnedBlueprint, OwnedBlueprintAdmin)
admin.site.register(InventionPolicy, InventionPolicyAdmin)
admin.site.register(ItemGroup, ItemGroupAdmin)
admin.site.register(PricingPolicy, PricingPolicyAdmin)

