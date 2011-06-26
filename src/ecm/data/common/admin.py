# Copyright (c) 2010-2011 Robin Jarry
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
'''
This file is part of EVE Corporation Management

Created on 17 mai 2010
@author: diabeteman
'''


from django.contrib import admin
from ecm.data.common.models import UpdateDate, ColorThreshold, APIKey, UserAPIKey, Url,\
    UserBinding, GroupBinding, ExternalApplication

class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'userID', 'charID', 'key']

class UserAPIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'userID', 'key', 'is_valid']

class ExternalAppAdmin(admin.ModelAdmin):
    list_display = ['name', 'url']

class UserBindingBindingAdmin(admin.ModelAdmin):
    list_display = ['external_app', 'user', 'external_id', 'external_name']

class GroupBindingBindingAdmin(admin.ModelAdmin):
    list_display = ['external_app', 'group', 'external_id', 'external_name']

class UpdateDateAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'update_date', 'prev_update']
    
class ColorTresholdAdmin(admin.ModelAdmin):
    list_display = ['color', 'threshold']

class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "content_type", "codename"]

class UrlAdmin(admin.ModelAdmin):
    list_display = ["pattern"]

admin.site.register(APIKey, APIKeyAdmin)
admin.site.register(UserAPIKey, UserAPIKeyAdmin)
admin.site.register(ExternalApplication, ExternalAppAdmin)
admin.site.register(UserBinding, UserBindingBindingAdmin)
admin.site.register(GroupBinding, GroupBindingBindingAdmin)
admin.site.register(UpdateDate, UpdateDateAdmin)
admin.site.register(ColorThreshold, ColorTresholdAdmin)
admin.site.register(Url, UrlAdmin)
