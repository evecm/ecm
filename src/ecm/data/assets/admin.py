'''
This file is part of ICE Security Management

Created on 14 mai 2010
@author: diabeteman
'''

from django.contrib import admin
from esm.data.assets.models import DbAsset, DbAssetDiff

class DbAssetAdmin(admin.ModelAdmin):
    list_display = ['itemID', 'locationID', 'hangarID', 'container1', 'container2', 
                    'typeID', 'quantity', 'flag', 'singleton', 'hasContents']

class DbAssetDiffAdmin(admin.ModelAdmin):
    list_display = ['locationID', 'hangarID', 'typeID', 'quantity', 'date', 'new']
    


admin.site.register(DbAsset, DbAssetAdmin)
admin.site.register(DbAssetDiff, DbAssetDiffAdmin)
