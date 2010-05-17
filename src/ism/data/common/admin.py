'''
This file is part of ICE Security Management

Created on 17 mai 2010
@author: diabeteman
'''


from django.contrib import admin, databrowse
from ism.data.common.models import UpdateDate

class UpdateDateAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'update_date', 'prev_update']
    
    
admin.site.register(UpdateDate, UpdateDateAdmin)
databrowse.site.register(UpdateDate)
