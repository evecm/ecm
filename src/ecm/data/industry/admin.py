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
from django.contrib import admin
from ecm.data.industry.models import Order, OrderComment, OrderRow, Job,\
                                    FactorySlot, ProductionSite, OwnedBlueprint

__date__ = "2011 6 9"
__author__ = "diabeteman"


#------------------------------------------------------------------------------
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "originator",
        "manufacturer",
        "deliveryMan",
        "client",
        "deliveryLocation",
        "deliveryDate",
        "state",
        "discount",
        "quote",
    ]
    
#------------------------------------------------------------------------------
class OrderCommentAdmin(admin.ModelAdmin):
    list_display = ["order", "state", "date", "user", "text",]
    
#------------------------------------------------------------------------------
class OrderRowAdmin(admin.ModelAdmin):
    list_display = ["itemID", "quantity", "order",]
    
#------------------------------------------------------------------------------
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "parentJob",
        "state",
        "factory",
        "owner",
        "itemID",
        "quantity",
        "blueprint",
        "activity",
        "duration",
        "deliveryDate",
        "startDate",
        "endDate",
    ]

#------------------------------------------------------------------------------
class ProductionSiteAdmin(admin.ModelAdmin):
    list_display = ["locationID", "customName", "discount",]
    
#------------------------------------------------------------------------------
class FactorySlotAdmin(admin.ModelAdmin):
    list_display = ["site", "activity",]

#------------------------------------------------------------------------------
class OwnedBlueprintAdmin(admin.ModelAdmin):
    list_display = [
        "blueprintID",
        "count",
        "original",
        "me",
        "pe",
    ]
    
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderComment, OrderCommentAdmin)
admin.site.register(OrderRow, OrderRowAdmin)
admin.site.register(Job, JobAdmin)
admin.site.register(FactorySlot, FactorySlotAdmin)
admin.site.register(ProductionSite, ProductionSiteAdmin)
admin.site.register(OwnedBlueprint, OwnedBlueprintAdmin)
