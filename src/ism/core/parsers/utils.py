"""
This file is part of ICE Security Management

Created on 08 fev. 2010
@author: diabeteman
"""

from ism.data.roles.models import RoleType, Role
from ism.settings import EVE_API_VERSION
from ism.data.common.models import UpdateDate
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist



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
    if version != EVE_API_VERSION:
        raise DeprecationWarning("Wrong EVE API version. Expected '%s', got '%s'." % (EVE_API_VERSION, version))
    
#------------------------------------------------------------------------------   
def calcDiffs(oldItems, newItems):
    """
    Quick way to compare 2 hashtables.
    
    This method returns 2 lists, added and removed items 
    when comparing the old and the new set
    """
    
    removed  = []
    added    = []

    for item in oldItems.values():
        try:
            newItems[item] # is "item" still in the newItems?
        except KeyError: # KeyError -> "item" has disappeared
            removed.append(item)
    for item in newItems.values():
        try:
            oldItems[item] # was "item" in the oldItems already?
        except KeyError: # KeyError -> "item" is new
            added.append(item)

    return removed, added

#------------------------------------------------------------------------------   
def markUpdated(model, date):
    """
    Tag a model's table in the database as 'updated'
    With the update date and the previous update date as well.
    """
    try:
        update = UpdateDate.objects.get(model_name=model.__name__)
        if not update.update_date == date:
            update.prev_update = update.update_date
            update.update_date = date
            update.save()
    except ObjectDoesNotExist:
        update = UpdateDate(model_name=model.__name__, update_date=date).save()
    except MultipleObjectsReturned:
        raise Exception
