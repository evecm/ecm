'''
This file is part of EVE Corporation Management

Created on 11 feb. 2010
@author: diabeteman
'''
from ecm.data.roles.models import RoleMembership, TitleMembership, RoleMemberDiff, \
    TitleMemberDiff, Member
from ecm.core.api import connection
from ecm.core.parsers import utils
from ecm import settings

from django.db import transaction

import logging.config

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("parser_membersecu")

#------------------------------------------------------------------------------
@transaction.commit_manually
def update():
    """
    Retrieve all corp members' titles and roles.
    We store all the changes in the database
    
    If there's an error, nothing is written in the database
    """
    
    try:
        logger.info("fetching /corp/MemberSecurity.xml.aspx...")
        # connect to eve API
        api = connection.connect()
        # retrieve /corp/MemberTracking.xml.aspx
        memberSecuApi = api.corp.MemberSecurity(characterID=connection.get_api().charID)
        utils.checkApiVersion(memberSecuApi._meta.version)
        
        currentTime = memberSecuApi._meta.currentTime
        cachedUntil = memberSecuApi._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))
        
        logger.debug("parsing api response...")
        oldRoles  = {}
        oldTitles = {}
        
        # we fetch the old data from the database
        for role in RoleMembership.objects.all():
            oldRoles[role] = role
        for title in TitleMembership.objects.all():
            oldTitles[title] = title
        
        newRoles  = {}
        newTitles = {}
        
        for member in memberSecuApi.members:
            # A.update(B) works as a merge of 2 hashtables A and B in A
            # if a key is already present in A, it takes B's value
            newRoles.update(parseOneMemberRoles(member)) 
            newTitles.update(parseOneMemberTitles(member))
        
        # Store role changes 
        roleDiffs = storeRoles(oldRoles, newRoles, currentTime)
        
        # Store title changes 
        titleDiffs = storeTitles(oldTitles, newTitles, currentTime)
        logger.info("%d role changes, %d title changes", roleDiffs, titleDiffs)
       
        # update members access levels
        for m in Member.objects.all():
            m.accessLvl = m.getAccessLvl()
            m.extraRoles = len(m.getRoles(ignore_director=True))
            m.save() 

        logger.debug("saving data to the database...")
        transaction.commit()
        logger.debug("DATABASE UPDATED!")
        logger.info("member roles/titles updated")

    except Exception, e:
        # error catched, rollback changes
        transaction.rollback()
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        logger.error("".join(errortrace))
        raise

#------------------------------------------------------------------------------

ROLE_TYPES = utils.roleTypes()
ALL_ROLES  = utils.allRoles()

def parseOneMemberRoles(member):
    roles = {}
    # we get the character ID so we can link the memberships to him
    memberID = member.characterID
    
    for roleCategory in ROLE_TYPES.values() :
        # we analyse each role category for this member
        for role in member[roleCategory.typeName] :
            # each role has a sub id within its category
            roleSubID = role.roleID
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
    
    for title in member.titles:
        membership = TitleMembership(member_id=memberID, title_id=title.titleID)
        titles[membership] = membership
            
    return titles

#------------------------------------------------------------------------------
def __storeRoleDiffs(removed, added, date):
    diffs    = []
    logger.debug("REMOVED ROLES:")
    if not removed : 
        logger.debug("(none)")
    for remrole in removed:
        logger.debug("- " + unicode(remrole))
        diffs.append(RoleMemberDiff(role_id   = remrole.role_id, 
                                    member_id = remrole.member_id, 
                                    new=False, date=date))
    logger.debug("ADDED ROLES:")
    if not added : 
        logger.debug("(none)")
    for addrole in added:
        logger.debug("+ " + unicode(addrole))
        diffs.append(RoleMemberDiff(role_id   = addrole.role_id, 
                                    member_id = addrole.member_id, 
                                    new=True, date=date))
        
    return diffs

def getRoleMemberDiffs(oldRoles, newRoles, date):
    removed, added = utils.calcDiffs(newItems=newRoles, oldItems=oldRoles)
    return __storeRoleDiffs(removed, added, date)
#------------------------------------------------------------------------------
def __storeTitleDiffs(removed, added, date):
    diffs = []
    logger.debug("REMOVED TITLES:")
    if not removed: 
        logger.debug("(none)")
    for remtitle in removed:
        logger.debug("- " + unicode(remtitle))
        diffs.append(TitleMemberDiff(title_id=remtitle.title_id, 
                                     member_id=remtitle.member_id, 
                                     new=False, date=date))
    
    logger.debug("ADDED TITLES:")
    if not added: 
        logger.debug("(none)")
    for addtitle in added:
        logger.debug("+ " + unicode(addtitle))
        diffs.append(TitleMemberDiff(title_id=addtitle.title_id, 
                                     member_id=addtitle.member_id, 
                                     new=True, date=date))
    
    return diffs

def getTitleMemberDiffs(oldTitles, newTitles, date):
    removed, added = utils.calcDiffs(newItems=newTitles, oldItems=oldTitles)
    return __storeTitleDiffs(removed, added, date)
#------------------------------------------------------------------------------
def storeRoles(oldRoles, newRoles, date):
    if len(oldRoles) != 0:
        roleDiffs = getRoleMemberDiffs(oldRoles, newRoles, date)
        if roleDiffs:
            for d in roleDiffs: d.save()
            # we store the update time of the table
            utils.markUpdated(model=RoleMemberDiff, date=date)
            
            RoleMembership.objects.all().delete()
            for rm in newRoles.values(): rm.save()
            # we store the update time of the table
            utils.markUpdated(model=RoleMembership, date=date)
        # if no diff, we do nothing
        return len(roleDiffs)
    else:
        # 1st import, no diff to write
        for rm in newRoles.values(): rm.save()
        # we store the update time of the table
        utils.markUpdated(model=RoleMembership, date=date)
        return 0

#------------------------------------------------------------------------------
def storeTitles(oldTitles, newTitles, date):
    if len(oldTitles) != 0:
        titleDiffs = getTitleMemberDiffs(oldTitles, newTitles, date)
        if titleDiffs:
            for d in titleDiffs: 
                d.save()
            # we store the update time of the table
            utils.markUpdated(model=TitleMemberDiff, date=date)
            
            TitleMembership.objects.all().delete()
            for tm in newTitles.values(): tm.save()
            # we store the update time of the table
            utils.markUpdated(model=TitleMembership, date=date)
        # if no diff, we do nothing
        return len(titleDiffs)
    else:
        # 1st import, no diff to write
        for tm in newTitles.values(): tm.save()
        # we store the update time of the table
        utils.markUpdated(model=TitleMembership, date=date)
        return 0
        
