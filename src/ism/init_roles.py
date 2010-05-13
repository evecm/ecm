'''
This file is part of ICE Security Management

Created on 24 jan. 2010
@author: diabeteman
'''


from ism.data.corp.models import Hangar, Wallet
from ism.data.roles.models import RoleType, Role
from django.db import transaction

@transaction.commit_manually
def init():
    #------------------#
    # HANGARS CREATION #
    #------------------#
    if not Hangar.objects.all():
        print "Creating hangar divisions..."
        Hangar(accessLvl=1000, hangarID=1000, name='Hangar 1').save()
        Hangar(accessLvl=1000, hangarID=1001, name='Hangar 2').save()
        Hangar(accessLvl=1000, hangarID=1002, name='Hangar 3').save()
        Hangar(accessLvl=1000, hangarID=1003, name='Hangar 4').save()
        Hangar(accessLvl=1000, hangarID=1004, name='Hangar 5').save()
        Hangar(accessLvl=1000, hangarID=1005, name='Hangar 6').save()
        Hangar(accessLvl=1000, hangarID=1006, name='Hangar 7').save()
    
    #------------------#
    # WALLETS CREATION #
    #------------------#
    if not Wallet.objects.all():
        print "Creating wallet divisions..."
        Wallet(accessLvl=1000, walletID=1000, name='Master Wallet').save()
        Wallet(accessLvl=1000, walletID=1001, name='Wallet 2').save()
        Wallet(accessLvl=1000, walletID=1002, name='Wallet 3').save()
        Wallet(accessLvl=1000, walletID=1003, name='Wallet 4').save()
        Wallet(accessLvl=1000, walletID=1004, name='Wallet 5').save()
        Wallet(accessLvl=1000, walletID=1005, name='Wallet 6').save()
        Wallet(accessLvl=1000, walletID=1006, name='Wallet 7').save()
    #---------------------#
    # ROLE TYPES CREATION #
    #---------------------#
    if not RoleType.objects.all():
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
    if not Role.objects.all():
        print "Creating roles..."
        Role( accessLvl=1000000, 
              roleID=1, 
              roleName="roleDirector", 
              dispName="Director", 
              description="Can do anything the CEO can do. Including giving roles to anyone.", 
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=50,
              roleID=128,
              roleName="rolePersonnelManager",
              dispName="Personnel Manager",
              description="Can accept applications to join the corporation.",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=40,
              roleID=256,
              roleName="roleAccountant",
              dispName="Accountant",
              description="Can view/use corporation accountancy info.",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=5,
              roleID=512,
              roleName="roleSecurityOfficer",
              dispName="Security Officer",
              description="Can view the content of other members hangars " + \
                          "(in stations where the corporation has an office)",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=50,
              roleID=1024,
              roleName="roleFactoryManager",
              dispName="Factory Manager",
              description="Can perform factory management tasks.",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=100,
              roleID=2048,
              roleName="roleStationManager",
              dispName="Station Manager",
              description="Can perform station management for a corporation.",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=50,
              roleID=4096,
              roleName="roleAuditor",
              dispName="Auditor",
              description="Can perform audits on corporation security event logs",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=100,
              roleID=134217728,
              roleName="roleAccountCanTake1",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='roles'),
              wallet=Wallet.objects.get(walletID=1000) ).save()
        Role( accessLvl=100,
              roleID=268435456,
              roleName="roleAccountCanTake2",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='roles'),
              wallet=Wallet.objects.get(walletID=1001) ).save()
        Role( accessLvl=100,
              roleID=536870912,
              roleName="roleAccountCanTake3",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='roles'),
              wallet=Wallet.objects.get(walletID=1002) ).save()
        Role( accessLvl=100,
              roleID=1073741824,
              roleName="roleAccountCanTake4",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='roles'),
              wallet=Wallet.objects.get(walletID=1003) ).save()
        Role( accessLvl=100,
              roleID=2147483648,
              roleName="roleAccountCanTake5",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='roles'),
              wallet=Wallet.objects.get(walletID=1004) ).save()
        Role( accessLvl=100,
              roleID=4294967296,
              roleName="roleAccountCanTake6",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='roles'),
              wallet=Wallet.objects.get(walletID=1005) ).save()
        Role( accessLvl=100,
              roleID=8589934592,
              roleName="roleAccountCanTake7",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='roles'),
              wallet=Wallet.objects.get(walletID=1006) ).save()
        Role( accessLvl=20,
              roleID=2199023255552,
              roleName="roleEquipmentConfig",
              dispName="Equipment Config",
              description="Can deploy and configure equipment in space.",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=20,
              roleID=562949953421312,
              roleName="roleCanRentOffice",
              dispName="Rent Office",
              description="When assigned to a member, " + \
                          "the member can rent offices on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=10,
              roleID=1125899906842624,
              roleName="roleCanRentFactorySlot",
              dispName="Rent Factory Slot",
              description="When assigned to a member, " + \
                          "the member can rent factory slots on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=10,
              roleID=2251799813685248,
              roleName="roleCanRentResearchSlot",
              dispName="Rent Research Slot",
              description="When assigned to a member, " + \
                          "the member can rent research facilities on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=10,
              roleID=4503599627370496,
              roleName="roleJuniorAccountant",
              dispName="Junior Accountant",
              description="Can view corporation accountancy info.",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=50,
              roleID=9007199254740992,
              roleName="roleStarbaseConfig",
              dispName="Starbase Config",
              description="Can deploy and configure starbase structures in space.",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=20,
              roleID=18014398509481984,
              roleName="roleTrader",
              dispName="Trader",
              description="Can buy and sell things on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=0,
              roleID=36028797018963968,
              roleName="roleChatManager",
              dispName="Communication Officer",
              description="Can moderate corporation/alliance communications channels",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=20,
              roleID=72057594037927936,
              roleName="roleContractManager",
              dispName="Contract Manager",
              description="Can create, edit and oversee all contracts made on behalf of the " + \
                          "corportation as well as accept contracts on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=10,
              roleID=144115188075855872,
              roleName="roleInfrastructureTacticalOfficer",
              dispName="Starbase Defence Operator",
              description="Can operate defensive starbase structures",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=10,
              roleID=288230376151711744,
              roleName="roleStarbaseCaretaker",
              dispName="Starbase Fuel Tech",
              description="Can refuel starbases and take from silo bins",
              roleType=RoleType.objects.get(typeName='roles') ).save()
        Role( accessLvl=20,
              roleID=576460752303423488,
              roleName="roleFittingManager",
              dispName="Fitting Manager",
              description="Can add and delete corporation fittings",
              roleType=RoleType.objects.get(typeName='roles') ).save()
    
        # grantableRoles
        print "Creating grantableRoles..."
        Role( accessLvl=50,
              roleID=128,
              roleName="rolePersonnelManager",
              dispName="Personnel Manager",
              description="Can accept applications to join the corporation.",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=40,
              roleID=256,
              roleName="roleAccountant",
              dispName="Accountant",
              description="Can view/use corporation accountancy info.",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=5,
              roleID=512,
              roleName="roleSecurityOfficer",
              dispName="Security Officer",
              description="Can view the content of other members hangars " + \
                          "(in stations where the corporation has an office)",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=50,
              roleID=1024,
              roleName="roleFactoryManager",
              dispName="Factory Manager",
              description="Can perform factory management tasks.",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=100,
              roleID=2048,
              roleName="roleStationManager",
              dispName="Station Manager",
              description="Can perform station management for a corporation.",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=50,
              roleID=4096,
              roleName="roleAuditor",
              dispName="Auditor",
              description="Can perform audits on corporation security event logs",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=100,
              roleID=134217728,
              roleName="roleAccountCanTake1",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='grantableRoles'),
              wallet=Wallet.objects.get(walletID=1000) ).save()
        Role( accessLvl=100,
              roleID=268435456,
              roleName="roleAccountCanTake2",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='grantableRoles'),
              wallet=Wallet.objects.get(walletID=1001) ).save()
        Role( accessLvl=100,
              roleID=536870912,
              roleName="roleAccountCanTake3",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='grantableRoles'),
              wallet=Wallet.objects.get(walletID=1002) ).save()
        Role( accessLvl=100,
              roleID=1073741824,
              roleName="roleAccountCanTake4",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='grantableRoles'),
              wallet=Wallet.objects.get(walletID=1003) ).save()
        Role( accessLvl=100,
              roleID=2147483648,
              roleName="roleAccountCanTake5",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='grantableRoles'),
              wallet=Wallet.objects.get(walletID=1004) ).save()
        Role( accessLvl=100,
              roleID=4294967296,
              roleName="roleAccountCanTake6",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='grantableRoles'),
              wallet=Wallet.objects.get(walletID=1005) ).save()
        Role( accessLvl=100,
              roleID=8589934592,
              roleName="roleAccountCanTake7",
              dispName="Account Take: %s",
              description="Can take funds from this divisions account",
              roleType=RoleType.objects.get(typeName='grantableRoles'),
              wallet=Wallet.objects.get(walletID=1006) ).save()
        Role( accessLvl=40,
              roleID=2199023255552,
              roleName="roleEquipmentConfig",
              dispName="Equipment Config",
              description="Can deploy and configure equipment in space.",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=10,
              roleID=562949953421312,
              roleName="roleCanRentOffice",
              dispName="Rent Office",
              description="When assigned to a member, " + \
                          "the member can rent offices on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=10,
              roleID=1125899906842624,
              roleName="roleCanRentFactorySlot",
              dispName="Rent Factory Slot",
              description="When assigned to a member, " + \
                          "the member can rent factory slots on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=10,
              roleID=2251799813685248,
              roleName="roleCanRentResearchSlot",
              dispName="Rent Research Slot",
              description="When assigned to a member, " + \
                          "the member can rent research facilities on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=10,
              roleID=4503599627370496,
              roleName="roleJuniorAccountant",
              dispName="Junior Accountant",
              description="Can view corporation accountancy info.",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=50,
              roleID=9007199254740992,
              roleName="roleStarbaseConfig",
              dispName="Starbase Config",
              description="Can deploy and configure starbase structures in space.",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=20,
              roleID=18014398509481984,
              roleName="roleTrader",
              dispName="Trader",
              description="Can buy and sell things on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=0,
              roleID=36028797018963968,
              roleName="roleChatManager",
              dispName="Communication Officer",
              description="Can moderate corporation/alliance communications channels",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=20,
              roleID=72057594037927936,
              roleName="roleContractManager",
              dispName="Contract Manager",
              description="Can create, edit and oversee all contracts made on behalf of the " + \
                          "corportation as well as accept contracts on behalf of the corporation",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=20,
              roleID=144115188075855872,
              roleName="roleInfrastructureTacticalOfficer",
              dispName="Starbase Defence Operator",
              description="Can operate defensive starbase structures",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=10,
              roleID=288230376151711744,
              roleName="roleStarbaseCaretaker",
              dispName="Starbase Fuel Tech",
              description="Can refuel starbases and take from silo bins",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
        Role( accessLvl=20,
              roleID=576460752303423488,
              roleName="roleFittingManager",
              dispName="Fitting Manager",
              description="Can add and delete corporation fittings",
              roleType=RoleType.objects.get(typeName='grantableRoles') ).save()
    
        # rolesAtHQ
        print "Creating rolesAtHQ..."
        Role( accessLvl=1000000,
              roleID=1,
              roleName="roleDirector",
              dispName="Director",
              description="Can do anything the CEO can do. Including giving roles to anyone.",
              roleType=RoleType.objects.get(typeName='rolesAtHQ') ).save()
        Role( accessLvl=100,
              roleID=8192,
              roleName="roleHangarCanTake1",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=16384,
              roleName="roleHangarCanTake2",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=32768,
              roleName="roleHangarCanTake3",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=65536,
              roleName="roleHangarCanTake4",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=131072,
              roleName="roleHangarCanTake5",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=262144,
              roleName="roleHangarCanTake6",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=524288,
              roleName="roleHangarCanTake7",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=1048576,
              roleName="roleHangarCanQuery1",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=2097152,
              roleName="roleHangarCanQuery2",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=4194304,
              roleName="roleHangarCanQuery3",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=8388608,
              roleName="roleHangarCanQuery4",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=16777216,
              roleName="roleHangarCanQuery5",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=33554432,
              roleName="roleHangarCanQuery6",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=67108864,
              roleName="roleHangarCanQuery7",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=4398046511104,
              roleName="roleContainerCanTake1",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=8796093022208,
              roleName="roleContainerCanTake2",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=17592186044416,
              roleName="roleContainerCanTake3",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=35184372088832,
              roleName="roleContainerCanTake4",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=70368744177664,
              roleName="roleContainerCanTake5",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=140737488355328,
              roleName="roleContainerCanTake6",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=281474976710656,
              roleName="roleContainerCanTake7",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
    
        # grantableRolesAtHQ
        print "Creating grantableRolesAtHQ..."
        Role( accessLvl=100,
              roleID=8192,
              roleName="roleHangarCanTake1",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=16384,
              roleName="roleHangarCanTake2",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=32768,
              roleName="roleHangarCanTake3",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=65536,
              roleName="roleHangarCanTake4",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=131072,
              roleName="roleHangarCanTake5",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=262144,
              roleName="roleHangarCanTake6",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=524288,
              roleName="roleHangarCanTake7",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=1048576,
              roleName="roleHangarCanQuery1",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=2097152,
              roleName="roleHangarCanQuery2",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=4194304,
              roleName="roleHangarCanQuery3",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=8388608,
              roleName="roleHangarCanQuery4",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=16777216,
              roleName="roleHangarCanQuery5",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=33554432,
              roleName="roleHangarCanQuery6",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=67108864,
              roleName="roleHangarCanQuery7",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=4398046511104,
              roleName="roleContainerCanTake1",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=8796093022208,
              roleName="roleContainerCanTake2",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=17592186044416,
              roleName="roleContainerCanTake3",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=35184372088832,
              roleName="roleContainerCanTake4",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=70368744177664,
              roleName="roleContainerCanTake5",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=140737488355328,
              roleName="roleContainerCanTake6",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=281474976710656,
              roleName="roleContainerCanTake7",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtHQ'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
    
        # rolesAtBase
        print "Creating rolesAtBase..."
        Role( accessLvl=1000000,
              roleID=1,
              roleName="roleDirector",
              dispName="Director",
              description="Can do anything the CEO can do. Including giving roles to anyone.",
              roleType=RoleType.objects.get(typeName='rolesAtBase') ).save()
        Role( accessLvl=100,
              roleID=8192,
              roleName="roleHangarCanTake1",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=16384,
              roleName="roleHangarCanTake2",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=32768,
              roleName="roleHangarCanTake3",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=65536,
              roleName="roleHangarCanTake4",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=131072,
              roleName="roleHangarCanTake5",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=262144,
              roleName="roleHangarCanTake6",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=524288,
              roleName="roleHangarCanTake7",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=1048576,
              roleName="roleHangarCanQuery1",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=2097152,
              roleName="roleHangarCanQuery2",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=4194304,
              roleName="roleHangarCanQuery3",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=8388608,
              roleName="roleHangarCanQuery4",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=16777216,
              roleName="roleHangarCanQuery5",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=33554432,
              roleName="roleHangarCanQuery6",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=67108864,
              roleName="roleHangarCanQuery7",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=4398046511104,
              roleName="roleContainerCanTake1",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=8796093022208,
              roleName="roleContainerCanTake2",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=17592186044416,
              roleName="roleContainerCanTake3",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=35184372088832,
              roleName="roleContainerCanTake4",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=70368744177664,
              roleName="roleContainerCanTake5",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=140737488355328,
              roleName="roleContainerCanTake6",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=281474976710656,
              roleName="roleContainerCanTake7",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
    
        # grantableRolesAtBase
        print "Creating grantableRolesAtBase..."
        Role( accessLvl=100,
              roleID=8192,
              roleName="roleHangarCanTake1",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=16384,
              roleName="roleHangarCanTake2",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=32768,
              roleName="roleHangarCanTake3",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=65536,
              roleName="roleHangarCanTake4",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=131072,
              roleName="roleHangarCanTake5",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=262144,
              roleName="roleHangarCanTake6",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=524288,
              roleName="roleHangarCanTake7",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=1048576,
              roleName="roleHangarCanQuery1",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=2097152,
              roleName="roleHangarCanQuery2",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=4194304,
              roleName="roleHangarCanQuery3",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=8388608,
              roleName="roleHangarCanQuery4",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=16777216,
              roleName="roleHangarCanQuery5",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=33554432,
              roleName="roleHangarCanQuery6",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=67108864,
              roleName="roleHangarCanQuery7",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=4398046511104,
              roleName="roleContainerCanTake1",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=8796093022208,
              roleName="roleContainerCanTake2",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=17592186044416,
              roleName="roleContainerCanTake3",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=35184372088832,
              roleName="roleContainerCanTake4",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=70368744177664,
              roleName="roleContainerCanTake5",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=140737488355328,
              roleName="roleContainerCanTake6",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=281474976710656,
              roleName="roleContainerCanTake7",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtBase'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
    
        # rolesAtOther
        print "Creating rolesAtOther..."
        Role( accessLvl=1000000,
              roleID=1,
              roleName="roleDirector",
              dispName="Director",
              description="Can do anything the CEO can do. Including giving roles to anyone.",
              roleType=RoleType.objects.get(typeName='rolesAtOther') ).save()
        Role( accessLvl=100,
              roleID=8192,
              roleName="roleHangarCanTake1",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=16384,
              roleName="roleHangarCanTake2",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=32768,
              roleName="roleHangarCanTake3",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=65536,
              roleName="roleHangarCanTake4",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=131072,
              roleName="roleHangarCanTake5",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=262144,
              roleName="roleHangarCanTake6",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=524288,
              roleName="roleHangarCanTake7",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=1048576,
              roleName="roleHangarCanQuery1",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=2097152,
              roleName="roleHangarCanQuery2",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=4194304,
              roleName="roleHangarCanQuery3",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=8388608,
              roleName="roleHangarCanQuery4",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=16777216,
              roleName="roleHangarCanQuery5",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=33554432,
              roleName="roleHangarCanQuery6",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=67108864,
              roleName="roleHangarCanQuery7",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=4398046511104,
              roleName="roleContainerCanTake1",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=8796093022208,
              roleName="roleContainerCanTake2",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=17592186044416,
              roleName="roleContainerCanTake3",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=35184372088832,
              roleName="roleContainerCanTake4",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=70368744177664,
              roleName="roleContainerCanTake5",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=140737488355328,
              roleName="roleContainerCanTake6",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=281474976710656,
              roleName="roleContainerCanTake7",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='rolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
    
        # grantableRolesAtOther
        print "Creating grantableRolesAtOther..."
        Role( accessLvl=100,
              roleID=8192,
              roleName="roleHangarCanTake1",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=16384,
              roleName="roleHangarCanTake2",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=32768,
              roleName="roleHangarCanTake3",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=65536,
              roleName="roleHangarCanTake4",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=131072,
              roleName="roleHangarCanTake5",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=262144,
              roleName="roleHangarCanTake6",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=524288,
              roleName="roleHangarCanTake7",
              dispName="Hangar Take: %s",
              description="Can take items from this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=1048576,
              roleName="roleHangarCanQuery1",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=2097152,
              roleName="roleHangarCanQuery2",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=4194304,
              roleName="roleHangarCanQuery3",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=8388608,
              roleName="roleHangarCanQuery4",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=16777216,
              roleName="roleHangarCanQuery5",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=33554432,
              roleName="roleHangarCanQuery6",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=67108864,
              roleName="roleHangarCanQuery7",
              dispName="Hangar Query: %s",
              description="Can query the content of this divisions hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        Role( accessLvl=100,
              roleID=4398046511104,
              roleName="roleContainerCanTake1",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1000) ).save()
        Role( accessLvl=100,
              roleID=8796093022208,
              roleName="roleContainerCanTake2",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1001) ).save()
        Role( accessLvl=100,
              roleID=17592186044416,
              roleName="roleContainerCanTake3",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1002) ).save()
        Role( accessLvl=100,
              roleID=35184372088832,
              roleName="roleContainerCanTake4",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1003) ).save()
        Role( accessLvl=100,
              roleID=70368744177664,
              roleName="roleContainerCanTake5",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1004) ).save()
        Role( accessLvl=100,
              roleID=140737488355328,
              roleName="roleContainerCanTake6",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1005) ).save()
        Role( accessLvl=100,
              roleID=281474976710656,
              roleName="roleContainerCanTake7",
              dispName="Container Take: %s",
              description="Can take containers from this divisional hangar",
              roleType=RoleType.objects.get(typeName='grantableRolesAtOther'),
              hangar=Hangar.objects.get(hangarID=1006) ).save()
        
    print ""
    
    transaction.commit()
    
if __name__ == "__main__" :
    init()
    
