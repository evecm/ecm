'''
This file is part of EVE Corporation Management

Created on 14 may 2010
@author: diabeteman
'''
from django.contrib import admin, databrowse
from ecm.data.corp.models import Hangar, Wallet

class HangarAdmin(admin.ModelAdmin):
    list_display = ['hangarID', 'name']

class WalletAdmin(admin.ModelAdmin):
    list_display = ['walletID', 'name']

admin.site.register(Hangar, HangarAdmin)
admin.site.register(Wallet, WalletAdmin)
databrowse.site.register(Hangar)
databrowse.site.register(Wallet)