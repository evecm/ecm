'''
This file is part of ICE Security Management

Created on 24 janv. 2010

@author: diabeteman
'''

from ISM.roles.models import RoleType, Role, Hangar
from django.db import transaction

@transaction.commit_manually
def init():
    #---------------------#
    #   HANGARS CREATION  #
    #---------------------#
    print "Creating hangars..."
    Hangar(hangarID=1, name='Dirlo').save()
    Hangar(hangarID=2, name='Starbase').save()
    Hangar(hangarID=3, name='Navy').save()
    Hangar(hangarID=4, name='FreStuff').save()
    Hangar(hangarID=5, name='Ships').save()
    Hangar(hangarID=6, name='BP').save()
    Hangar(hangarID=7, name='Prod').save()
    
    #---------------------#
    # ROLE TYPES CREATION #
    #---------------------#
    print "Creating role categories..."
    RoleType(typeName='roles').save()
    RoleType(typeName='grantableRoles').save()
    RoleType(typeName='rolesAtHQ').save()
    RoleType(typeName='grantableRolesAtHQ').save()
    RoleType(typeName='rolesAtBase').save()
    RoleType(typeName='grantableRolesAtBase').save()
    RoleType(typeName='rolesAtOther').save()
    RoleType(typeName='grantableRolesAtOther').save()
    
    #----------------#
    # ROLES CREATION #
    #----------------#
    # roles
    print "Creating roles..."
    Role(roleID=1, roleName="roleDirector", description="Can do anything the CEO can do. Including giving roles to anyone.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=128, roleName="rolePersonnelManager", description="Can accept applications to join the corporation.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=256, roleName="roleAccountant", description="Can view/use corporation accountancy info.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=512, roleName="roleSecurityOfficer", description="Can view the content of others hangars", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=1024, roleName="roleFactoryManager", description="Can perform factory management tasks.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=2048, roleName="roleStationManager", description="Can perform station management for a corporation.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=4096, roleName="roleAuditor", description="Can perform audits on corporation security event logs", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=134217728, roleName="roleAccountCanTake1", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=268435456, roleName="roleAccountCanTake2", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=536870912, roleName="roleAccountCanTake3", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=1073741824, roleName="roleAccountCanTake4", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=2147483648, roleName="roleAccountCanTake5", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=4294967296, roleName="roleAccountCanTake6", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=8589934592, roleName="roleAccountCanTake7", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=2199023255552, roleName="roleEquipmentConfig", description="Can deploy and configure equipment in space.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=562949953421312, roleName="roleCanRentOffice", description="When assigned to a member, the member can rent offices on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=1125899906842624, roleName="roleCanRentFactorySlot", description="When assigned to a member, the member can rent factory slots on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=2251799813685248, roleName="roleCanRentResearchSlot", description="When assigned to a member, the member can rent research facilities on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=4503599627370496, roleName="roleJuniorAccountant", description="Can view corporation accountancy info.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=9007199254740992, roleName="roleStarbaseConfig", description="Can deploy and configure starbase structures in space.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=18014398509481984, roleName="roleTrader", description="Can buy and sell things for the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=36028797018963968, roleName="roleChatManager", description="Can moderate corporation/alliance communications channels", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=72057594037927936, roleName="roleContractManager", description="Can create, edit and oversee all contracts made on behalf of the corportation as well as accept contracts on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=144115188075855872, roleName="roleInfrastructureTacticalOfficer", description="Can operate defensive starbase structures", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=288230376151711744, roleName="roleStarbaseCaretaker", description="Can refuel starbases and take from silo bins", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=576460752303423488, roleName="roleFittingManager", description="Can add and delete fittings", roleType=RoleType.objects.get(typeName='roles')).save()

    # grantableRoles
    print "Creating grantableRoles..."
    Role(roleID=128, roleName="rolePersonnelManager", description="Can accept applications to join the corporation.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=256, roleName="roleAccountant", description="Can view/use corporation accountancy info.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=512, roleName="roleSecurityOfficer", description="Can view the content of others hangars", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=1024, roleName="roleFactoryManager", description="Can perform factory management tasks.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=2048, roleName="roleStationManager", description="Can perform station management for a corporation.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=4096, roleName="roleAuditor", description="Can perform audits on corporation security event logs", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=134217728, roleName="roleAccountCanTake1", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=268435456, roleName="roleAccountCanTake2", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=536870912, roleName="roleAccountCanTake3", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=1073741824, roleName="roleAccountCanTake4", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=2147483648, roleName="roleAccountCanTake5", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=4294967296, roleName="roleAccountCanTake6", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=8589934592, roleName="roleAccountCanTake7", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=2199023255552, roleName="roleEquipmentConfig", description="Can deploy and configure equipment in space.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=562949953421312, roleName="roleCanRentOffice", description="When assigned to a member, the member can rent offices on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=1125899906842624, roleName="roleCanRentFactorySlot", description="When assigned to a member, the member can rent factory slots on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=2251799813685248, roleName="roleCanRentResearchSlot", description="When assigned to a member, the member can rent research facilities on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=4503599627370496, roleName="roleJuniorAccountant", description="Can view corporation accountancy info.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=9007199254740992, roleName="roleStarbaseConfig", description="Can deploy and configure starbase structures in space.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=18014398509481984, roleName="roleTrader", description="Can buy and sell things for the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=36028797018963968, roleName="roleChatManager", description="Can moderate corporation/alliance communications channels", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=72057594037927936, roleName="roleContractManager", description="Can create, edit and oversee all contracts made on behalf of the corportation as well as accept contracts on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=144115188075855872, roleName="roleInfrastructureTacticalOfficer", description="Can operate defensive starbase structures", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=288230376151711744, roleName="roleStarbaseCaretaker", description="Can refuel starbases and take from silo bins", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=576460752303423488, roleName="roleFittingManager", description="Can add and delete fittings", roleType=RoleType.objects.get(typeName='grantableRoles')).save()

    # rolesAtHQ
    print "Creating rolesAtHQ..."
    Role(roleID=1, roleName="roleDirector", description="Can do anything the CEO can do. Including giving roles to anyone.", roleType=RoleType.objects.get(typeName='rolesAtHQ')).save()
    Role(roleID=8192, roleName="roleHangarCanTake1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=7)).save()

    # grantableRolesAtHQ
    print "Creating grantableRolesAtHQ..."
    Role(roleID=8192, roleName="roleHangarCanTake1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=7)).save()

    # rolesAtBase
    print "Creating rolesAtBase..."
    Role(roleID=1, roleName="roleDirector", description="Can do anything the CEO can do. Including giving roles to anyone.", roleType=RoleType.objects.get(typeName='rolesAtBase')).save()
    Role(roleID=8192, roleName="roleHangarCanTake1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=7)).save()

    # grantableRolesAtBase
    print "Creating grantableRolesAtBase..."
    Role(roleID=8192, roleName="roleHangarCanTake1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=7)).save()

    # rolesAtOther
    print "Creating rolesAtOther..."
    Role(roleID=1, roleName="roleDirector", description="Can do anything the CEO can do. Including giving roles to anyone.", roleType=RoleType.objects.get(typeName='rolesAtOther')).save()
    Role(roleID=8192, roleName="roleHangarCanTake1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=7)).save()

    # grantableRolesAtOther
    print "Creating grantableRolesAtOther..."
    Role(roleID=8192, roleName="roleHangarCanTake1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=7)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=2)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=3)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=4)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=5)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=6)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=7)).save()
    
    transaction.commit()
