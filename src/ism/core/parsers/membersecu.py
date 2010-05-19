'''
This file is part of ICE Security Management

Created on 11 feb. 2010
@author: diabeteman
'''
from ism.data.roles.models import RoleMembership, TitleMembership, RoleMemberDiff, \
    TitleMemberDiff
from ism.core.api import connection
from ism.core.api.connection import API
from ism.core.parsers import utils
from django.db import transaction
from ism.core.parsers.utils import checkApiVersion, calcDiffs, markUpdated

from datetime import datetime

DEBUG = False # DEBUG mode

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(debug=False):
    """
    Retrieve all corp members' titles and roles.
    We store all the changes in the database
    
    If there's an error, nothing is written in the database
    """
    global DEBUG
    DEBUG = debug
    
    try:
        # connect to eve API
        api = connection.connect(debug=debug)
        # retrieve /corp/MemberTracking.xml.aspx
        memberSecuApi = api.corp.MemberSecurity(characterID=API.CHAR_ID)
        checkApiVersion(memberSecuApi._meta.version)
        
        currentTime = memberSecuApi._meta.currentTime
        cachedUntil = memberSecuApi._meta.cachedUntil
        if DEBUG : print "current time : %s" % str(datetime.fromtimestamp(currentTime))
        if DEBUG : print "cached util  : %s" % str(datetime.fromtimestamp(cachedUntil))
        
        oldRoles  = {}
        oldTitles = {}
        
        # we fetch the old data from the database
        for role in RoleMembership.objects.all():
            oldRoles[role] = role
        for title in TitleMembership.objects.all():
            oldTitles[title] = title
        
        newRoles  = {}
        newTitles = {}
        
        for member in memberSecuApi.member:
            # A.update(B) works as a merge of 2 hashtables A and B in A
            # if a key is already present in A, it takes B's value
            newRoles.update(parseOneMemberRoles(member)) 
            newTitles.update(parseOneMemberTitles(member))
        
        # Store role changes 
        roleDiffs = storeRoles(currentTime, oldRoles, newRoles)
        
        # Store title changes 
        titleDiffs = storeTitles(currentTime, oldTitles, newTitles)
        
        if DEBUG : print "saving data to the database..."
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"

        return "%s [ISM] %d role changes, %d title changes" % (str(datetime.now()), 
                                                                  roleDiffs, titleDiffs)
    except:
        transaction.rollback()
        raise

#------------------------------------------------------------------------------
def parseOneMemberRoles(member):
    roles = {}
    
    ROLE_TYPES = utils.roleTypes()
    ALL_ROLES  = utils.allRoles()
    # we get the character ID so we can link the memberships to him
    memberID = member["characterID"]
    
    for roleCategory in ROLE_TYPES.values() :
        # we analyse each role category for this member
        for role in member[roleCategory.typeName] :
            # each role has a sub id within its category
            roleSubID = role["roleID"]
            # we have to resolve the global role id from the category id and the role sub id.
            globalRoleID = ALL_ROLES[(roleSubID, roleCategory.id)].id
            # then we can create a new membership item for the current member and this role
            membership = RoleMembership(member_id=memberID, role_id=globalRoleID)
            roles[membership] = membership
    
    return roles

#------------------------------------------------------------------------------
def parseOneMemberTitles(member):
    titles = {}
    
    # we get the character ID so we can link the memberships to him
    memberID = member["characterID"]
    
    for title in member["titles"] :
        titleID = title["titleID"]
        membership = TitleMembership(member_id=memberID, title_id=titleID)
        titles[membership] = membership
            
    return titles

#------------------------------------------------------------------------------
def __storeRoleDiffs(date, removed, added):
    diffs    = []
    if DEBUG:
        print "REMOVED ROLES:"
        if not removed : print "(none)"
    for remrole in removed:
        if DEBUG: print "- " + unicode(remrole)
        diffs.append(RoleMemberDiff(role_id   = remrole.role_id, 
                                    member_id = remrole.member_id, 
                                    new=False, date=date))
    if DEBUG:
        print "ADDED ROLES:"
        if not added : print "(none)"
    for addrole in added:
        if DEBUG: print "+ " + unicode(addrole)
        diffs.append(RoleMemberDiff(role_id   = addrole.role_id, 
                                    member_id = addrole.member_id, 
                                    new=True, date=date))
        
    return diffs

def getRoleMemberDiffs(newTitles, oldTitles, date):
    removed, added = calcDiffs(newItems=newTitles, oldItems=oldTitles)
    return __storeRoleDiffs(date, removed, added)
#------------------------------------------------------------------------------
def __storeTitleDiffs(date, removed, added):
    diffs = []
    if DEBUG:
        print "REMOVED TITLES:"
        if not removed: print "(none)"
    for remtitle in removed:
        if DEBUG: print "- " + unicode(remtitle)
        diffs.append(TitleMemberDiff(title_id=remtitle.title_id, 
                                     member_id=remtitle.member_id, 
                                     new=False, date=date))
    
    if DEBUG:
        print "ADDED TITLES:"
        if not added: print "(none)"
    for addtitle in added:
        if DEBUG: print "+ " + unicode(addtitle)
        diffs.append(TitleMemberDiff(title_id=addtitle.title_id, 
                                     member_id=addtitle.member_id, 
                                     new=True, date=date))
    
    return diffs

def getTitleMemberDiffs(newTitles, oldTitles, date):
    removed, added = calcDiffs(newItems=newTitles, oldItems=oldTitles)
    return __storeTitleDiffs(date, removed, added)
#------------------------------------------------------------------------------
def storeRoles(date, oldRoles, newRoles):
    if len(oldRoles) != 0:
        roleDiffs = getRoleMemberDiffs(date, oldRoles, newRoles)
        if roleDiffs:
            for d in roleDiffs: d.save()
            # we store the update time of the table
            markUpdated(model=RoleMemberDiff, date_int=date)
            
            RoleMembership.objects.all().delete()
            for rm in newRoles.values(): rm.save()
            # we store the update time of the table
            markUpdated(model=RoleMembership, date_int=date)
        # if no diff, we do nothing
        return len(roleDiffs)
    else:
        # 1st import, no diff to write
        for rm in newRoles.values(): rm.save()
        # we store the update time of the table
        markUpdated(model=RoleMembership, date_int=date)
        return 0

#------------------------------------------------------------------------------
def storeTitles(date, oldTitles, newTitles):
    if len(oldTitles) != 0:
        titleDiffs = getTitleMemberDiffs(newTitles, oldTitles, date)
        if titleDiffs:
            for d in titleDiffs: d.save()
            # we store the update time of the table
            markUpdated(model=TitleMemberDiff, date_int=date)
            
            TitleMembership.objects.all().delete()
            for tm in newTitles.values(): tm.save()
            # we store the update time of the table
            markUpdated(model=TitleMembership, date_int=date)
        # if no diff, we do nothing
        return len(roleDiffs)
    else:
        # 1st import, no diff to write
        for tm in newTitles.values(): tm.save()
        # we store the update time of the table
        markUpdated(model=TitleMembership, date_int=date)
        return 0
        
