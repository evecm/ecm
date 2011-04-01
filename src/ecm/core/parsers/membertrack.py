# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2010-02-09"
__author__ = "diabeteman"



from django.db import transaction
from ecm.data.roles.models import Member, MemberDiff
from ecm.core import api
from ecm.core.parsers import utils
from ecm.core.db import resolveLocationName

import logging
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
        membersApi = api_conn.corp.MemberTracking(characterID=api.get_api().charID)
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
    
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")
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
    
