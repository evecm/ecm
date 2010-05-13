"""
This file is part of ICE Security Management

Created on 08 fev. 2010
@author: diabeteman
"""

from ism.server.data.roles.models import RoleType, Role
from ism.server.logic.exceptions import WrongApiVersion
from ism.constants import API_VERSION

_ROLE_TYPES = None
_ALL_ROLES = None

#------------------------------------------------------------------------------
def roleTypes():
    global _ROLE_TYPES
    if _ROLE_TYPES == None:
        _ROLE_TYPES = {}
        for type in RoleType.objects.all() :
            _ROLE_TYPES[type.typeName] = type
    return _ROLE_TYPES

#------------------------------------------------------------------------------
def allRoles():
    global _ALL_ROLES
    if _ALL_ROLES == None:
        _ALL_ROLES = {}
        for role in Role.objects.all() :
            _ALL_ROLES[(role.roleID, role.roleType_id)] = role
    return _ALL_ROLES

#------------------------------------------------------------------------------
def checkApiVersion(version):
    if version != API_VERSION:
        print version
        raise WrongApiVersion(version)
    
#------------------------------------------------------------------------------   
def calcDiffs(newItems, oldItems):
    """
    Quick way to compare 2 hashtables.
    
    This method returns 2 lists, added and removed items 
    when comparing the old and the new set
    """
    
    removed  = []
    added    = []

    for a in oldItems.values():
        try:
            newItems[a] # is a still in the newItems?
        except KeyError: # KeyError -> a has disappeared
            removed.append(a)
    for a in newItems.values():
        try:
            oldItems[a] # was a in the oldItems already?
        except KeyError: # KeyError -> a is new
            added.append(a)

    return removed, added

