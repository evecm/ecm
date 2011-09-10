# Copyright (c) 2010-2011 Robin Jarry
# 
# This file is part of EVE Corporation Management.
# 
# EVE Corporation Management is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# EVE Corporation Management is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
# 
# You should have received a copy of the GNU General Public License along with 
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2010-02-09"
__author__ = "diabeteman"


import logging

from django.db import transaction

from ecm.core.eve import api
from ecm.core.eve import db
from ecm.core.parsers import checkApiVersion, calcDiffs, markUpdated
from ecm.data.roles.models import Member, MemberDiff

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_manually
def update():
    """
    Retrieve all corp members, with all basic information about them.
    If some members have left or have arrived we also store the diff in the database.
    
    If there's an error, nothing is written in the database
    """
    
    try:
        logger.info("fetching /corp/MemberTracking.xml.aspx...")
        # connect to eve API
        api_conn = api.connect()
        # retrieve /corp/MemberTracking.xml.aspx
        membersApi = api_conn.corp.MemberTracking(characterID=api.get_api().characterID)
        checkApiVersion(membersApi._meta.version)
        
        currentTime = membersApi._meta.currentTime
        cachedUntil = membersApi._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))
        
        logger.debug("parsing api response...")
        newMembers = {}
        oldMembers = {}
        notCorped  = {}
        oldAccessLvls = {}
        oldOwners = {}
        
        # we get the old member list from the database
        for m in Member.objects.all(): 
            if m.corped:
                oldMembers[m] = m
            else:
                notCorped[m] = m
            oldAccessLvls[m.characterID] = m.accessLvl
            oldOwners[m.characterID] = m.owner
            
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
                m.owner = oldOwners[m.characterID]
            except KeyError:
                # 'm' is a brand new member, his/her access level didn't exist before
                # we leave it to the default value '0'
                continue

        if len(oldMembers) > 0 and len(diffs) > 0 :
            for d in diffs:
                d.save()
            # we store the update time of the table
            markUpdated(model=MemberDiff, date=currentTime)
        # to be sure to store the nicknames change, etc.
        # even if there are no diff, we always overwrite the members 
        for m in newMembers.values():
            m.save()
        # we store the update time of the table
        markUpdated(model=Member, date=currentTime)
        
        logger.debug("saving to database...")
        transaction.commit()
        logger.debug("DATABASE UPDATED!")
        logger.info("members updated")
    
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")
        raise


#------------------------------------------------------------------------------
def parseOneMember(member):
    return Member(characterID   = member.characterID,    
                  name          = member.name,         
                  nickname      = member.title,
                  baseID        = member.baseID,       
                  corpDate      = member.startDateTime, 
                  lastLogin     = member.logonDateTime,
                  lastLogoff    = member.logoffDateTime, 
                  location      = db.resolveLocationName(member.locationID)[0], 
                  locationID    = member.locationID, 
                  ship          = member.shipType)
    
#------------------------------------------------------------------------------
def getDiffs(oldMembers, newMembers, date):
    removed, added = calcDiffs(oldItems=oldMembers, newItems=newMembers)
    
    diffs  = []
    
    logger.debug("RESIGNED MEMBERS:")
    if not removed : logger.debug("(none)")
    for oldmember in removed:
        logger.debug("- %s (%s)", oldmember.name, oldmember.nickname)
        diffs.append(MemberDiff(member_id   = oldmember.characterID, 
                                name        = oldmember.name,
                                nickname    = oldmember.nickname, 
                                new=False, date=date))
    logger.debug("NEW MEMBERS:")
    if not added : logger.debug("(none)")
    for newmember in added:
        logger.debug("+ %s (%s)", newmember.name, newmember.nickname)
        diffs.append(MemberDiff(member_id   = newmember.characterID, 
                                name        = newmember.name,
                                nickname    = newmember.nickname, 
                                new=True, date=date))
    return diffs, removed
    
