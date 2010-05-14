'''
This file is part of ICE Security Management

Created on 14 mai 2010
@author: diabeteman
'''

from django.contrib import admin, databrowse
from ism.data.assets.models import DbAsset, DbAssetDiff, Outpost

class DbAssetAdmin(admin.ModelAdmin):
    list_display = ['itemID', 'locationID', 'hangarID', 'container1', 'container2', 
                    'typeID', 'quantity', 'flag', 'singleton', 'hasContents']

class DbAssetDiffAdmin(admin.ModelAdmin):
    list_display = ['locationID', 'hangarID', 'typeID', 'quantity', 'date', 'new']
    
class OutpostAdmin(admin.ModelAdmin):
    list_display = ['stationID', 'stationName', 'stationTypeID', 'solarSystemID', 
                    'corporationID', 'corporationName']

admin.site.register(DbAsset, DbAssetAdmin)
admin.site.register(DbAssetDiff, DbAssetDiffAdmin)
admin.site.register(Outpost, OutpostAdmin)
databrowse.site.register(DbAsset)
databrowse.site.register(DbAssetDiff)
databrowse.site.register(Outpost)
