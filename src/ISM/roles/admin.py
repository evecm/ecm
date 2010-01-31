'''
This file is part of ICE Security Management

Created on 24 janv. 2010

@author: diabeteman
'''

from ISM.roles.models import Role, Character, Title, RoleType, RoleMembership, TitleMembership, TitleComposition, Hangar
from django.contrib import admin
from django.contrib import databrowse

admin.site.register(Hangar)
admin.site.register(Role)
admin.site.register(Title)
admin.site.register(Character)
admin.site.register(RoleType)
admin.site.register(RoleMembership)
admin.site.register(TitleMembership)
admin.site.register(TitleComposition)

databrowse.site.register(Hangar)
databrowse.site.register(Role)
databrowse.site.register(Title)
databrowse.site.register(Character)
databrowse.site.register(RoleType)
databrowse.site.register(RoleMembership)
databrowse.site.register(TitleMembership)
databrowse.site.register(TitleComposition)
