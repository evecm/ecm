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

__date__ = "2010-01-24"
__author__ = "diabeteman"



from ecm.data.roles.models import Role, Title, Member, RoleType, RoleMembership, MemberDiff,\
    TitleCompoDiff, TitleMemberDiff, RoleMemberDiff, TitleMembership, TitleComposition, CharacterOwnership
from django.contrib import admin

class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'characterID', 'nickname', 'baseID', 'lastLogin', 'corpDate']
    search_fields = ['name', 'baseID', 'nickname', 'lastLogin']
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
    list_display = ['name', 'characterID', 'nickname', 'date', 'new']
    search_fields = ['name', 'characterID', 'nickname', 'date']
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

class CharacterOwnershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'character', 'main_or_alt_admin_display']

admin.site.register(Member, MemberAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(RoleType, RoleTypeAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(RoleMembership, RoleMembershipAdmin)
admin.site.register(TitleMembership, TitleMembershipAdmin)
admin.site.register(MemberDiff, MemberDiffAdmin)
admin.site.register(CharacterOwnership, CharacterOwnershipAdmin)
admin.site.register(TitleComposition, TitleCompositionAdmin)
admin.site.register(TitleCompoDiff, TitleCompoDiffAdmin)
admin.site.register(TitleMemberDiff, TitleMemberDiffAdmin)
admin.site.register(RoleMemberDiff, RoleMemberDiffAdmin)

