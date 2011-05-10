# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''
This file is part of EVE Corporation Management

Created on 17 mai 2010
@author: diabeteman
'''


from django.contrib import admin
from ecm.data.common.models import UpdateDate, Outpost, ColorThreshold, APIKey, UserAPIKey, Url

class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'userID', 'charID', 'key']

class UserAPIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'userID', 'key', 'is_valid']

class UpdateDateAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'update_date', 'prev_update']
    
class OutpostAdmin(admin.ModelAdmin):
    list_display = ['stationID', 'stationName', 'stationTypeID', 'solarSystemID', 
                    'corporationID', 'corporationName']
class ColorTresholdAdmin(admin.ModelAdmin):
    list_display = ['color', 'threshold']

class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "content_type", "codename"]

class UrlAdmin(admin.ModelAdmin):
    list_display = ["pattern"]

admin.site.register(APIKey, APIKeyAdmin)
admin.site.register(UserAPIKey, UserAPIKeyAdmin)
admin.site.register(UpdateDate, UpdateDateAdmin)
admin.site.register(Outpost, OutpostAdmin)
admin.site.register(ColorThreshold, ColorTresholdAdmin)
admin.site.register(Url, UrlAdmin)
