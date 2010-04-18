'''
This file is part of ICE Security Management

Created on 11 feb. 2010
@author: diabeteman
'''
from ism.server.data.roles.models import RoleMembership, TitleMembership, RoleMemberDiff, \
    TitleMemberDiff
from ism.server.logic.api import connection
from ism.server.logic.api.connection import API
from ism.server.logic.parsers import utils
from django.db import transaction
from ism.server.logic.parsers.utils import checkApiVersion

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
        

        newRoleList = []
        newTitleList = []
        # we fetch the old data from the database
        oldRoleList = list(RoleMembership.objects.all())
        oldTitleList = list(TitleMembership.objects.all())
        
        for member in memberSecuApi.member:
            newRoleList.extend(parseOneMemberRoles(member))
            newTitleList.extend(parseOneMemberTitles(member))
        
        storeRoleDiffs(oldList=oldRoleList, newList=newRoleList, date=currentTime)
        storeTitleDiffs(oldList=oldTitleList, newList=newTitleList, date=currentTime)
        
        if DEBUG : print "saving data to the database..."
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"
    except:
        transaction.rollback()
        raise

#------------------------------------------------------------------------------
def parseOneMemberRoles(member):
    roleList = []
    
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
            roleList.append(RoleMembership(member_id=memberID, role_id=globalRoleID))
    
    return roleList

#------------------------------------------------------------------------------
def parseOneMemberTitles(member):
    titleList = []
    
    # we get the character ID so we can link the memberships to him
    memberID = member["characterID"]
    
    for title in member["titles"] :
        titleID = title["titleID"]
        titleList.append(TitleMembership(member_id=memberID, title_id=titleID))
            
    return titleList

#------------------------------------------------------------------------------
def getRoleMemberDiffs(newList, oldList, date):
    removed  = [ r for r in oldList if r not in newList ]
    added    = [ r for r in newList if r not in oldList ]
    
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
    
#------------------------------------------------------------------------------
def getTitleMemberDiffs(newList, oldList, date):
    removed  = [ t for t in oldList if t not in newList ]
    added    = [ t for t in newList if t not in oldList ]
    
    diffs    = []
    if DEBUG:
        print "REMOVED TITLES:"
        if not removed : print "(none)"
    for remtitle in removed:
        if DEBUG: print "- " + unicode(remtitle)
        diffs.append(TitleMemberDiff(title_id  = remtitle.title_id, 
                                     member_id = remtitle.member_id, 
                                     new=False, date=date))
    if DEBUG:
        print "ADDED TITLES:"
        if not added : print "(none)"
    for addtitle in added:
        if DEBUG: print "+ " + unicode(addtitle)
        diffs.append(TitleMemberDiff(title_id  = addtitle.title_id, 
                                     member_id = addtitle.member_id, 
                                     new=True, date=date))
        
    return diffs

#------------------------------------------------------------------------------
def storeRoleDiffs(oldList, newList, date):
    if len(oldList) != 0 :
        diffs = getRoleMemberDiffs(newList, oldList, date)
        if diffs :
            for d in diffs: d.save()
            RoleMembership.objects.all().delete()
            for rm in newList: rm.save()
        # if no diff, we do nothing
    else:
        # 1st import, no diff to write
        for rm in newList: rm.save()

#------------------------------------------------------------------------------
def storeTitleDiffs(oldList, newList, date):
    if len(oldList) != 0 :
        diffs = getTitleMemberDiffs(newList, oldList, date)
        if diffs :
            for d in diffs: d.save()
            TitleMembership.objects.all().delete()
            for tm in newList: tm.save()
        # if no diff, we do nothing
    else:
        # 1st import, no diff to write
        for tm in newList: tm.save()

