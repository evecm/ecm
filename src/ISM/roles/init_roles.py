'''
This file is part of ICE Security Management

Created on 24 janv. 2010
@author: diabeteman
'''

from ISM.roles.models import RoleType, Role, Hangar, Wallet
from django.db import transaction

@transaction.commit_manually
def init():
    #------------------#
    # HANGARS CREATION #
    #------------------#
    print "Creating hangar divisions..."
    Hangar(hangarID=1001, name='1. STARBASE').save()
    Hangar(hangarID=1002, name='2. SHIPS').save()
    Hangar(hangarID=1003, name='3. FREE STUFF').save()
    Hangar(hangarID=1004, name='4. DIRLOS').save()
    Hangar(hangarID=1005, name='5. BLUEPRINTS').save()
    Hangar(hangarID=1006, name='6. PRODUCTION').save()
    Hangar(hangarID=1007, name='7. NAVY').save()
    
    #------------------#
    # WALLETS CREATION #
    #------------------#
    print "Creating wallet divisions..."
    Wallet(walletID=1001, name='Master Wallet').save()
    Wallet(walletID=1002, name='2. Navy').save()
    Wallet(walletID=1003, name='3. POS').save()
    Wallet(walletID=1004, name='4. T1').save()
    Wallet(walletID=1005, name='5. T2').save()
    Wallet(walletID=1006, name='6. Capital').save()
    Wallet(walletID=1007, name='7. Jobs Corpo').save()
    #---------------------#
    # ROLE TYPES CREATION #
    #---------------------#
    print "Creating role categories..."
    RoleType(typeName='roles', dispName='General').save()
    RoleType(typeName='grantableRoles', dispName='Grantable General').save()
    RoleType(typeName='rolesAtHQ', dispName='At HQ').save()
    RoleType(typeName='grantableRolesAtHQ', dispName='Grantable At HQ').save()
    RoleType(typeName='rolesAtBase', dispName='At Base').save()
    RoleType(typeName='grantableRolesAtBase', dispName='Grantable At Base').save()
    RoleType(typeName='rolesAtOther', dispName='At Other').save()
    RoleType(typeName='grantableRolesAtOther', dispName='Grantable At Other').save()

    #----------------#
    # ROLES CREATION #
    #----------------#
    # roles
    print "Creating roles..."
    Role(roleID=1, roleName="roleDirector", dispName="Director", description="Can do anything the CEO can do. Including giving roles to anyone.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=128, roleName="rolePersonnelManager", dispName="Personnel Manager", description="Can accept applications to join the corporation.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=256, roleName="roleAccountant", dispName="Accountant", description="Can view/use corporation accountancy info.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=512, roleName="roleSecurityOfficer", dispName="Security Officer", description="Can view the content of other members hangars (in stations where the corporation has an office)", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=1024, roleName="roleFactoryManager", dispName="Factory Manager", description="Can perform factory management tasks.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=2048, roleName="roleStationManager", dispName="Station Manager", description="Can perform station management for a corporation.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=4096, roleName="roleAuditor", dispName="Auditor", description="Can perform audits on corporation security event logs", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=134217728, roleName="roleAccountCanTake1", dispName="Account Take 1", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), wallet=Wallet.objects.get(walletID=1001)).save()
    Role(roleID=268435456, roleName="roleAccountCanTake2", dispName="Account Take 2", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), wallet=Wallet.objects.get(walletID=1002)).save()
    Role(roleID=536870912, roleName="roleAccountCanTake3", dispName="Account Take 3", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), wallet=Wallet.objects.get(walletID=1003)).save()
    Role(roleID=1073741824, roleName="roleAccountCanTake4", dispName="Account Take 4", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), wallet=Wallet.objects.get(walletID=1004)).save()
    Role(roleID=2147483648, roleName="roleAccountCanTake5", dispName="Account Take 5", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), wallet=Wallet.objects.get(walletID=1005)).save()
    Role(roleID=4294967296, roleName="roleAccountCanTake6", dispName="Account Take 6", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), wallet=Wallet.objects.get(walletID=1006)).save()
    Role(roleID=8589934592, roleName="roleAccountCanTake7", dispName="Account Take 7", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='roles'), wallet=Wallet.objects.get(walletID=1007)).save()
    Role(roleID=2199023255552, roleName="roleEquipmentConfig", dispName="Equipment Config", description="Can deploy and configure equipment in space.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=562949953421312, roleName="roleCanRentOffice", dispName="Rent Office", description="When assigned to a member, the member can rent offices on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=1125899906842624, roleName="roleCanRentFactorySlot", dispName="Rent Factory Slot", description="When assigned to a member, the member can rent factory slots on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=2251799813685248, roleName="roleCanRentResearchSlot", dispName="Rent Research Slot", description="When assigned to a member, the member can rent research facilities on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=4503599627370496, roleName="roleJuniorAccountant", dispName="Junior Accountant", description="Can view corporation accountancy info.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=9007199254740992, roleName="roleStarbaseConfig", dispName="Starbase Config", description="Can deploy and configure starbase structures in space.", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=18014398509481984, roleName="roleTrader", dispName="Trader", description="Can buy and sell things on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=36028797018963968, roleName="roleChatManager", dispName="Communication Officer", description="Can moderate corporation/alliance communications channels", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=72057594037927936, roleName="roleContractManager", dispName="Contract Manager", description="Can create, edit and oversee all contracts made on behalf of the corportation as well as accept contracts on behalf of the corporation", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=144115188075855872, roleName="roleInfrastructureTacticalOfficer", dispName="Starbase Defence Operator", description="Can operate defensive starbase structures", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=288230376151711744, roleName="roleStarbaseCaretaker", dispName="Starbase Fuel Tech", description="Can refuel starbases and take from silo bins", roleType=RoleType.objects.get(typeName='roles')).save()
    Role(roleID=576460752303423488, roleName="roleFittingManager", dispName="Fitting Manager", description="Can add and delete corporation fittings", roleType=RoleType.objects.get(typeName='roles')).save()

    # grantableRoles
    print "Creating grantableRoles..."
    Role(roleID=128, roleName="rolePersonnelManager", dispName="Personnel Manager", description="Can accept applications to join the corporation.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=256, roleName="roleAccountant", dispName="Accountant", description="Can view/use corporation accountancy info.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=512, roleName="roleSecurityOfficer", dispName="Security Officer", description="Can view the content of other members hangars (in stations where the corporation has an office)", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=1024, roleName="roleFactoryManager", dispName="Factory Manager", description="Can perform factory management tasks.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=2048, roleName="roleStationManager", dispName="Station Manager", description="Can perform station management for a corporation.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=4096, roleName="roleAuditor", dispName="Auditor", description="Can perform audits on corporation security event logs", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=134217728, roleName="roleAccountCanTake1", dispName="Account Take 1", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), wallet=Wallet.objects.get(walletID=1001)).save()
    Role(roleID=268435456, roleName="roleAccountCanTake2", dispName="Account Take 2", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), wallet=Wallet.objects.get(walletID=1002)).save()
    Role(roleID=536870912, roleName="roleAccountCanTake3", dispName="Account Take 3", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), wallet=Wallet.objects.get(walletID=1003)).save()
    Role(roleID=1073741824, roleName="roleAccountCanTake4", dispName="Account Take 4", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), wallet=Wallet.objects.get(walletID=1004)).save()
    Role(roleID=2147483648, roleName="roleAccountCanTake5", dispName="Account Take 5", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), wallet=Wallet.objects.get(walletID=1005)).save()
    Role(roleID=4294967296, roleName="roleAccountCanTake6", dispName="Account Take 6", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), wallet=Wallet.objects.get(walletID=1006)).save()
    Role(roleID=8589934592, roleName="roleAccountCanTake7", dispName="Account Take 7", description="Can take funds from this divisions account", roleType=RoleType.objects.get(typeName='grantableRoles'), wallet=Wallet.objects.get(walletID=1007)).save()
    Role(roleID=2199023255552, roleName="roleEquipmentConfig", dispName="Equipment Config", description="Can deploy and configure equipment in space.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=562949953421312, roleName="roleCanRentOffice", dispName="Rent Office", description="When assigned to a member, the member can rent offices on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=1125899906842624, roleName="roleCanRentFactorySlot", dispName="Rent Factory Slot", description="When assigned to a member, the member can rent factory slots on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=2251799813685248, roleName="roleCanRentResearchSlot", dispName="Rent Research Slot", description="When assigned to a member, the member can rent research facilities on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=4503599627370496, roleName="roleJuniorAccountant", dispName="Junior Accountant", description="Can view corporation accountancy info.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=9007199254740992, roleName="roleStarbaseConfig", dispName="Starbase Config", description="Can deploy and configure starbase structures in space.", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=18014398509481984, roleName="roleTrader", dispName="Trader", description="Can buy and sell things on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=36028797018963968, roleName="roleChatManager", dispName="Communication Officer", description="Can moderate corporation/alliance communications channels", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=72057594037927936, roleName="roleContractManager", dispName="Contract Manager", description="Can create, edit and oversee all contracts made on behalf of the corportation as well as accept contracts on behalf of the corporation", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=144115188075855872, roleName="roleInfrastructureTacticalOfficer", dispName="Starbase Defence Operator", description="Can operate defensive starbase structures", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=288230376151711744, roleName="roleStarbaseCaretaker", dispName="Starbase Fuel Tech", description="Can refuel starbases and take from silo bins", roleType=RoleType.objects.get(typeName='grantableRoles')).save()
    Role(roleID=576460752303423488, roleName="roleFittingManager", dispName="Fitting Manager", description="Can add and delete corporation fittings", roleType=RoleType.objects.get(typeName='grantableRoles')).save()

    # rolesAtHQ
    print "Creating rolesAtHQ..."
    Role(roleID=1, roleName="roleDirector", dispName="Director", description="Can do anything the CEO can do. Including giving roles to anyone.", roleType=RoleType.objects.get(typeName='rolesAtHQ')).save()
    Role(roleID=8192, roleName="roleHangarCanTake1", dispName="Hangar Take 1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", dispName="Hangar Take 2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", dispName="Hangar Take 3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", dispName="Hangar Take 4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", dispName="Hangar Take 5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", dispName="Hangar Take 6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", dispName="Hangar Take 7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", dispName="Hangar Query 1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", dispName="Hangar Query 2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", dispName="Hangar Query 3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", dispName="Hangar Query 4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", dispName="Hangar Query 5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", dispName="Hangar Query 6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", dispName="Hangar Query 7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", dispName="Container Take 1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", dispName="Container Take 2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", dispName="Container Take 3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", dispName="Container Take 4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", dispName="Container Take 5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", dispName="Container Take 6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", dispName="Container Take 7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtHQ'), hangar=Hangar.objects.get(hangarID=1007)).save()

    # grantableRolesAtHQ
    print "Creating grantableRolesAtHQ..."
    Role(roleID=8192, roleName="roleHangarCanTake1", dispName="Hangar Take 1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", dispName="Hangar Take 2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", dispName="Hangar Take 3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", dispName="Hangar Take 4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", dispName="Hangar Take 5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", dispName="Hangar Take 6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", dispName="Hangar Take 7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", dispName="Hangar Query 1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", dispName="Hangar Query 2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", dispName="Hangar Query 3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", dispName="Hangar Query 4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", dispName="Hangar Query 5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", dispName="Hangar Query 6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", dispName="Hangar Query 7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", dispName="Container Take 1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", dispName="Container Take 2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", dispName="Container Take 3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", dispName="Container Take 4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", dispName="Container Take 5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", dispName="Container Take 6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", dispName="Container Take 7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'), hangar=Hangar.objects.get(hangarID=1007)).save()

    # rolesAtBase
    print "Creating rolesAtBase..."
    Role(roleID=1, roleName="roleDirector", dispName="Director", description="Can do anything the CEO can do. Including giving roles to anyone.", roleType=RoleType.objects.get(typeName='rolesAtBase')).save()
    Role(roleID=8192, roleName="roleHangarCanTake1", dispName="Hangar Take 1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", dispName="Hangar Take 2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", dispName="Hangar Take 3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", dispName="Hangar Take 4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", dispName="Hangar Take 5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", dispName="Hangar Take 6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", dispName="Hangar Take 7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", dispName="Hangar Query 1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", dispName="Hangar Query 2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", dispName="Hangar Query 3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", dispName="Hangar Query 4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", dispName="Hangar Query 5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", dispName="Hangar Query 6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", dispName="Hangar Query 7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", dispName="Container Take 1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", dispName="Container Take 2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", dispName="Container Take 3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", dispName="Container Take 4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", dispName="Container Take 5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", dispName="Container Take 6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", dispName="Container Take 7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtBase'), hangar=Hangar.objects.get(hangarID=1007)).save()

    # grantableRolesAtBase
    print "Creating grantableRolesAtBase..."
    Role(roleID=8192, roleName="roleHangarCanTake1", dispName="Hangar Take 1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", dispName="Hangar Take 2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", dispName="Hangar Take 3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", dispName="Hangar Take 4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", dispName="Hangar Take 5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", dispName="Hangar Take 6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", dispName="Hangar Take 7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", dispName="Hangar Query 1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", dispName="Hangar Query 2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", dispName="Hangar Query 3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", dispName="Hangar Query 4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", dispName="Hangar Query 5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", dispName="Hangar Query 6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", dispName="Hangar Query 7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", dispName="Container Take 1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", dispName="Container Take 2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", dispName="Container Take 3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", dispName="Container Take 4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", dispName="Container Take 5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", dispName="Container Take 6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", dispName="Container Take 7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtBase'), hangar=Hangar.objects.get(hangarID=1007)).save()

    # rolesAtOther
    print "Creating rolesAtOther..."
    Role(roleID=1, roleName="roleDirector", dispName="Director", description="Can do anything the CEO can do. Including giving roles to anyone.", roleType=RoleType.objects.get(typeName='rolesAtOther')).save()
    Role(roleID=8192, roleName="roleHangarCanTake1", dispName="Hangar Take 1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", dispName="Hangar Take 2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", dispName="Hangar Take 3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", dispName="Hangar Take 4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", dispName="Hangar Take 5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", dispName="Hangar Take 6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", dispName="Hangar Take 7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", dispName="Hangar Query 1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", dispName="Hangar Query 2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", dispName="Hangar Query 3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", dispName="Hangar Query 4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", dispName="Hangar Query 5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", dispName="Hangar Query 6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", dispName="Hangar Query 7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", dispName="Container Take 1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", dispName="Container Take 2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", dispName="Container Take 3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", dispName="Container Take 4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", dispName="Container Take 5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", dispName="Container Take 6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", dispName="Container Take 7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='rolesAtOther'), hangar=Hangar.objects.get(hangarID=1007)).save()

    # grantableRolesAtOther
    print "Creating grantableRolesAtOther..."
    Role(roleID=8192, roleName="roleHangarCanTake1", dispName="Hangar Take 1", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=16384, roleName="roleHangarCanTake2", dispName="Hangar Take 2", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=32768, roleName="roleHangarCanTake3", dispName="Hangar Take 3", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=65536, roleName="roleHangarCanTake4", dispName="Hangar Take 4", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=131072, roleName="roleHangarCanTake5", dispName="Hangar Take 5", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=262144, roleName="roleHangarCanTake6", dispName="Hangar Take 6", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=524288, roleName="roleHangarCanTake7", dispName="Hangar Take 7", description="Can take items from this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=1048576, roleName="roleHangarCanQuery1", dispName="Hangar Query 1", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=2097152, roleName="roleHangarCanQuery2", dispName="Hangar Query 2", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=4194304, roleName="roleHangarCanQuery3", dispName="Hangar Query 3", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=8388608, roleName="roleHangarCanQuery4", dispName="Hangar Query 4", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=16777216, roleName="roleHangarCanQuery5", dispName="Hangar Query 5", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=33554432, roleName="roleHangarCanQuery6", dispName="Hangar Query 6", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=67108864, roleName="roleHangarCanQuery7", dispName="Hangar Query 7", description="Can query the content of this divisions hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1007)).save()
    Role(roleID=4398046511104, roleName="roleContainerCanTake1", dispName="Container Take 1", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1001)).save()
    Role(roleID=8796093022208, roleName="roleContainerCanTake2", dispName="Container Take 2", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1002)).save()
    Role(roleID=17592186044416, roleName="roleContainerCanTake3", dispName="Container Take 3", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1003)).save()
    Role(roleID=35184372088832, roleName="roleContainerCanTake4", dispName="Container Take 4", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1004)).save()
    Role(roleID=70368744177664, roleName="roleContainerCanTake5", dispName="Container Take 5", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1005)).save()
    Role(roleID=140737488355328, roleName="roleContainerCanTake6", dispName="Container Take 6", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1006)).save()
    Role(roleID=281474976710656, roleName="roleContainerCanTake7", dispName="Container Take 7", description="Can take containers from this divisional hangar", roleType=RoleType.objects.get(typeName='grantableRolesAtOther'), hangar=Hangar.objects.get(hangarID=1007)).save()
    print ""
    
    transaction.commit()
