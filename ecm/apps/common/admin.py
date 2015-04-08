# Copyright (c) 2010-2012 Robin Jarry
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

__date__ = "2010-05-17"
__author__ = "diabeteman"


from django.contrib import admin
from ecm.apps.common.models import Setting, \
                                   ColorThreshold, \
                                   ExternalApplication, \
                                   GroupBinding, \
                                   RegistrationProfile, \
                                   UpdateDate, \
                                   UrlPermission, \
                                   UserAPIKey, \
                                   UserBinding, \
                                   APICall

class SettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    search_fields = ['name']
class ColorThresholdAdmin(admin.ModelAdmin):
    list_display = ['color', 'threshold']
    search_fields = []
class ExternalApplicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'url']
    search_fields = ['name']
class GroupBindingAdmin(admin.ModelAdmin):
    list_display = ['external_name', 'external_id', 'group', 'external_app']
    search_fields = ['external_name', 'group__name']
class UpdateDateAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'update_date', 'prev_update']
    search_fields = ['model_name']
class UrlPermissionAdmin(admin.ModelAdmin):
    list_display = ['pattern', 'groups_admin_display']
    search_fields = ['pattern']
    filter_horizontal = ['groups']
    ordering = ['id']
class UserAPIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'keyID', 'vCode', 'is_valid']
    search_fields = ['user__username']
class UserBindingAdmin(admin.ModelAdmin):
    list_display = ['external_name', 'external_id', 'user', 'external_app']
    search_fields = ['external_name', 'user__username']
class APICallAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'required', 'group', 'mask', 'description']
    search_fields = ['name', 'description']
    list_filter   = ['type', 'group']

admin.site.register(Setting, SettingAdmin)
admin.site.register(ColorThreshold, ColorThresholdAdmin)
admin.site.register(ExternalApplication, ExternalApplicationAdmin)
admin.site.register(GroupBinding, GroupBindingAdmin)
admin.site.register(RegistrationProfile)
admin.site.register(UpdateDate, UpdateDateAdmin)
admin.site.register(UrlPermission, UrlPermissionAdmin)
admin.site.register(UserAPIKey, UserAPIKeyAdmin)
admin.site.register(UserBinding, UserBindingAdmin)
admin.site.register(APICall, APICallAdmin)