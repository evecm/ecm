'''
This file is part of EVE Corporation Management

Created on 14 mai 2010
@author: diabeteman
'''
from django.contrib import admin, databrowse
from ecm.data.api.models import APIKey

class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'userID', 'charID', 'key']

admin.site.register(APIKey, APIKeyAdmin)
databrowse.site.register(APIKey)
