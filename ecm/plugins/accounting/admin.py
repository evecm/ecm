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

__date__ = "2010-06-03"
__author__ = "diabeteman"

# change test


from django.contrib import admin

from ecm.plugins.accounting.models import JournalEntry, EntryType, Contract, ContractItem, MarketOrder

class JournalEntryAdmin(admin.ModelAdmin):
    list_display  = ['wallet', 'date', 'type', 'ownerName1', 'ownerName2', 'amount', 'balance', 'reason']
    search_fields = ['ownerName1', 'ownerName2', 'date']
    list_filter   = ['wallet', 'type']
class EntryTypeAdmin(admin.ModelAdmin):
    list_display  = ['refTypeID', 'refTypeName']
    search_fields = ['refTypeName']
class ContractAdmin(admin.ModelAdmin):
    list_display  = ['type', 'status', 'title', 'issuerID', 'acceptorID', 'dateIssued', 'dateExpired', 
                     'dateAccepted', 'dateCompleted', 'price', 'reward', 'collateral', 'buyout', 'volume']
    search_fields = ['title']
    list_filter   = ['type', 'status']
class ContractItemAdmin(admin.ModelAdmin):
    list_display  = ['recordID', 'typeID', 'quantity', 'rawQuantity', 'singleton', 'included']
    search_fields = ['recordID', 'typeID']
    list_filter   = []
class MarketOrderAdmin(admin.ModelAdmin):
    list_display  = ['orderID', 'charID', 'typeID', 'price', 'stationID', 'volRemaining', 'volEntered', 'minVolume', ]
    search_fields = ['typeID']
    list_filter   = ['typeID']

admin.site.register(JournalEntry, JournalEntryAdmin)
admin.site.register(EntryType, EntryTypeAdmin)
admin.site.register(Contract, ContractAdmin)
admin.site.register(ContractItem, ContractItemAdmin)
admin.site.register(MarketOrder, MarketOrderAdmin)
