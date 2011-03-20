'''
This file is part of EVE Corporation Management

Created on 9 feb. 2010
@author: diabeteman
'''
from django.db import transaction
from ecm.data.roles.models import Member, MemberDiff
from ecm.core.api import connection
from ecm.core.api.connection import API
from ecm.core.parsers import utils
from ecm.core.db import resolveLocationName
from ecm import settings

import logging.config

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("parser_membertrack")

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(cache=False):
    """
    Retrieve all corp members, with all basic information about them.
    If some members have left or have arrived we also store the diff in the database.
    
    If there's an error, nothing is written in the database
    """
    
    try:
        logger.info("fetching /corp/MemberTracking.xml.aspx...")
        # connect to eve API
        api = connection.connect(cache=cache)
        # retrieve /corp/MemberTracking.xml.aspx
        membersApi = api.corp.MemberTracking(characterID=API.CHAR_ID)
        utils.checkApiVersion(membersApi._meta.version)
        
        currentTime = membersApi._meta.currentTime
        cachedUntil = membersApi._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))
        
        logger.debug("parsing api response...")
        newMembers = {}
        oldMembers = {}
        notCorped  = {}
        oldAccessLvls = {}
        
        # we get the old member list from the database
        for m in Member.objects.all(): 
            if m.corped:
                oldMembers[m] = m
            else:
                notCorped[m] = m
            oldAccessLvls[m.characterID] = m.accessLvl
            
        for member in membersApi.members:
            m = parseOneMember(member=member)
            newMembers[m] = m
        
        diffs, leaved = getDiffs(oldMembers, newMembers, currentTime)
        # "leaved" is the list of members that leaved (not a list of MemberDiff but real Member objects)
        # If we delete the old members each time, then all the diffs in roles/titles will not match
        # as the foreign keys will be gone from the members table... 
        for L in leaved: 
            L.corped = False
            newMembers[L] = L
            
        logger.info("%d members parsed, %d changes since last scan", len(newMembers), len(diffs))

        for m in notCorped.values():
            try:
                # if the previously "not corped" members can now be found in the "new members"
                # we do nothing
                newMembers[m]
            except KeyError:
                # if the previously "not corped" members still cannot be found in the "new members"
                # we add them again to the members list
                newMembers[m] = m
        
        for m in newMembers.values():
            try: 
                # we restore the old access levels from the database
                m.accessLvl = oldAccessLvls[m.characterID]
            except KeyError:
                # 'm' is a brand new member, his/her access level didn't exist before
                # we leave it to the default value '0'
                continue

        if len(oldMembers) > 0 and len(diffs) > 0 :
            for d in diffs:
                d.save()
            # we store the update time of the table
            utils.markUpdated(model=MemberDiff, date=currentTime)
        # to be sure to store the nicknames change, etc.
        # even if there are no diff, we always overwrite the members 
        for m in newMembers.values():
            m.save()
        # we store the update time of the table
        utils.markUpdated(model=Member, date=currentTime)
        
        logger.debug("saving to database...")
        transaction.commit()
        logger.debug("DATABASE UPDATED!")
        logger.info("members updated")
    
    except Exception, e:
        # error catched, rollback changes
        transaction.rollback()
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        logger.error("".join(errortrace))
        raise


#------------------------------------------------------------------------------
def parseOneMember(member):
    id       = member["characterID"]
    name     = member["name"]
    nick     = member["title"]
    corpDate = member["startDateTime"]
    base     = member["baseID"]
    login    = member["logonDateTime"]
    logoff   = member["logoffDateTime"]
    location = resolveLocationName(member["locationID"])
    ship     = member["shipType"]
    
    return Member(characterID=id,    name=name,         nickname=nick,
                  baseID=base,       corpDate=corpDate, lastLogin=login,
                  lastLogoff=logoff, location=location, ship=ship)
    
#------------------------------------------------------------------------------
def getDiffs(oldMembers, newMembers, date):
    removed, added = utils.calcDiffs(oldItems=oldMembers, newItems=newMembers)
    
    diffs  = []
    
    logger.debug("RESIGNED MEMBERS:")
    if not removed : logger.debug("(none)")
    for oldmember in removed:
        logger.debug("- %s (%s)", oldmember.name, oldmember.nickname)
        diffs.append(MemberDiff(characterID = oldmember.characterID, 
                                name        = oldmember.name,
                                nickname    = oldmember.nickname, 
                                new=False, date=date))
    logger.debug("NEW MEMBERS:")
    if not removed : logger.debug("(none)")
    for newmember in added:
        logger.debug("+ %s (%s)", newmember.name, newmember.nickname)
        diffs.append(MemberDiff(characterID = newmember.characterID, 
                                name        = newmember.name,
                                nickname    = newmember.nickname, 
                                new=True, date=date))
    return diffs, removed
    
