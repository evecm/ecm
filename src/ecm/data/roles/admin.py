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

__date__ = "2010-01-24"
__author__ = "diabeteman"



from ecm.data.roles.models import Role, Title, Member, RoleType, RoleMembership, MemberDiff,\
    TitleCompoDiff, TitleMemberDiff, RoleMemberDiff, TitleMembership, TitleComposition
from django.contrib import admin

class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'characterID', 'nickname', 'owner', 'baseID', 'lastLogin', 'corpDate']
    search_fields = ['name', 'baseID', 'nickname', 'owner', 'lastLogin']
    list_filter = ['baseID']

class RoleAdmin(admin.ModelAdmin):
    fields = ['dispName', 'description', 'roleType']
    list_display = ['dispName', 'hangar', 'wallet', 'roleType', 'description']
    search_fields = ['roleType']
    list_filter = ['roleType']

class TitleAdmin(admin.ModelAdmin):
    list_display = ['titleName', 'tiedToBase']

class RoleTypeAdmin(admin.ModelAdmin):
    list_display = ['typeName', 'dispName']

class RoleMembershipAdmin(admin.ModelAdmin):
    list_display = ['member', 'role']
    list_filter = ['member', 'role']

class TitleMembershipAdmin(admin.ModelAdmin):
    list_display = ['member', 'title']
    list_filter = ['member', 'title']

class TitleCompositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'role']
    list_filter = ['title', 'role']

class MemberDiffAdmin(admin.ModelAdmin):
    list_display = ['member', 'nickname', 'date', 'new']
    search_fields = ['member', 'nickname', 'date']
    list_filter = ['date']

class TitleCompoDiffAdmin(admin.ModelAdmin):
    list_display = ['title', 'role', 'new', 'date']
    search_fields = ['title', 'role', 'new', 'date']

class TitleMemberDiffAdmin(admin.ModelAdmin):
    list_display = ['member', 'title', 'new', 'date']
    search_fields = ['member', 'title', 'new', 'date']

class RoleMemberDiffAdmin(admin.ModelAdmin):
    list_display = ['member', 'role', 'new', 'date']
    search_fields = ['member', 'role', 'new', 'date']


admin.site.register(Member, MemberAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(RoleType, RoleTypeAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(RoleMembership, RoleMembershipAdmin)
admin.site.register(TitleMembership, TitleMembershipAdmin)
admin.site.register(MemberDiff, MemberDiffAdmin)
admin.site.register(TitleComposition, TitleCompositionAdmin)
admin.site.register(TitleCompoDiff, TitleCompoDiffAdmin)
admin.site.register(TitleMemberDiff, TitleMemberDiffAdmin)
admin.site.register(RoleMemberDiff, RoleMemberDiffAdmin)

