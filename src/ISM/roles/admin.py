'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

from ISM.roles.models import Role, Member, Title, RoleType, RoleMembership, TitleMembership, TitleComposition, Hangar, Wallet

from django.contrib import admin
from django.contrib import databrowse

class RoleAdmin(admin.ModelAdmin):
    fields = ['dispName', 'description', 'roleType']
    list_display = ['dispName', 'hangar', 'wallet', 'roleType', 'description']
    search_fields = ['roleType']
    list_filter = ['roleType']

class TitleAdmin(admin.ModelAdmin):
    list_display = ['titleName', 'tiedToBase']

class HangarAdmin(admin.ModelAdmin):
    list_display = ['hangarID', 'name']

class WalletAdmin(admin.ModelAdmin):
    list_display = ['walletID', 'name']

class MemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'characterID', 'nickname', 'baseID', 'lastLogin', 'corpDate']
    search_fields = ['name', 'baseID', 'nickname', 'lastLogin']
    list_filter = ['baseID']

class RoleMembershipAdmin(admin.ModelAdmin):
    list_display = ['member', 'roleName', 'roleType']
    search_fields = ['member', 'role']
    list_filter = ['member', 'role']

class TitleMembershipAdmin(admin.ModelAdmin):
    list_display = ['member', 'title']
    search_fields = ['member', 'title']
    list_filter = ['member', 'title']

class TitleCompositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'roleName', 'roleType', 'hangar', 'wallet']
    search_fields = ['title', 'role']
    list_filter = ['title', 'role']

admin.site.register(Role, RoleAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(RoleType)
admin.site.register(Hangar, HangarAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(RoleMembership, RoleMembershipAdmin)
admin.site.register(TitleMembership, TitleMembershipAdmin)
admin.site.register(TitleComposition, TitleCompositionAdmin)

databrowse.site.register(Role)
databrowse.site.register(Title)
databrowse.site.register(Member)
databrowse.site.register(RoleType)
databrowse.site.register(Hangar)
databrowse.site.register(RoleMembership)
databrowse.site.register(TitleMembership)
databrowse.site.register(TitleComposition)

