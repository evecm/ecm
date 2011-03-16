'''
This file is part of ICE Security Management

Created on 3 juin 2010
@author: diabeteman
'''


from esm.data.wallets.models import JournalEntry
from django.contrib import admin

#------------------------------------------------------------------------------

class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'date', 'refTypeID', 'ownerName1', 'ownerName2', 'amount', 'balance', 'reason']
    search_fields = ['wallet', 'ownerName1', 'ownerName2', 'date']
    list_filter = ['wallet']
    
admin.site.register(JournalEntry, JournalEntryAdmin)
