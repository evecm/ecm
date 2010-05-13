'''
This file is part of ICE Security Management

Created on 24 jan. 2010

@author: diabeteman
'''

from ism.data.corp.models import Hangar, Wallet
from ism.data.roles.models import Role, Title, Member, RoleType, RoleMembership, \
    TitleMembership, TitleComposition
from django.contrib import admin, databrowse


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

admin.site.register(Role, RoleAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(RoleType)
admin.site.register(Hangar, HangarAdmin)
admin.site.register(Wallet, WalletAdmin)

databrowse.site.register(Role)
databrowse.site.register(Title)
databrowse.site.register(Member)
databrowse.site.register(RoleType)
databrowse.site.register(Hangar)
databrowse.site.register(RoleMembership)
databrowse.site.register(TitleMembership)
databrowse.site.register(TitleComposition)

