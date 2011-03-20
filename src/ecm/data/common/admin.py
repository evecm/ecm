'''
This file is part of ICE Security Management

Created on 17 mai 2010
@author: diabeteman
'''


from django.contrib import admin
from esm.data.common.models import UpdateDate, RefType, Outpost, ColorThreshold
from django.contrib.auth.models import Permission

class UpdateDateAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'update_date', 'prev_update']
    
class RefTypeAdmin(admin.ModelAdmin):
    list_display = ['refTypeID', 'refTypeName']
    
class OutpostAdmin(admin.ModelAdmin):
    list_display = ['stationID', 'stationName', 'stationTypeID', 'solarSystemID', 
                    'corporationID', 'corporationName']
class ColorTresholdAdmin(admin.ModelAdmin):
    list_display = ['color', 'threshold']

class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "content_type", "codename"]

admin.site.register(UpdateDate, UpdateDateAdmin)
admin.site.register(RefType, RefTypeAdmin)
admin.site.register(Outpost, OutpostAdmin)
admin.site.register(ColorThreshold, ColorTresholdAdmin)
admin.site.register(Permission, PermissionAdmin)
