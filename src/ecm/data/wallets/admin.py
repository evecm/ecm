'''
This file is part of EVE Corporation Management

Created on 3 juin 2010
@author: diabeteman
'''


from ecm.data.wallets.models import AccountingEntry
from django.contrib import admin

#------------------------------------------------------------------------------

class AccountingEntryAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'date', 'type', 'ownerName1', 'ownerName2', 'amount', 'balance', 'reason']
    search_fields = ['ownerName1', 'ownerName2', 'date']
    list_filter = ['wallet', 'type']
    
admin.site.register(AccountingEntry, AccountingEntryAdmin)
