'''
This file is part of ICE Security Management

Created on 9 feb. 2010
@author: diabeteman
'''
from django.db import transaction
from ism.data.roles.models import Member, MemberDiff
from ism.core.api import connection
from ism.core.api.connection import API
from ism.core.parsers import utils


DEBUG = False # DEBUG mode

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(debug=False, cache=False):
    """
    Retrieve all corp members, with all basic information about them.
    If some members have left or have arrived we also store the diff in the database.
    
    If there's an error, nothing is written in the database
    """
    global DEBUG
    DEBUG = debug
    
    try:
        # connect to eve API
        api = connection.connect(debug=debug, cache=cache)
        # retrieve /corp/MemberTracking.xml.aspx
        membersApi = api.corp.MemberTracking(characterID=API.CHAR_ID)
        utils.checkApiVersion(membersApi._meta.version)
        
        currentTime = membersApi._meta.currentTime
        cachedUntil = membersApi._meta.cachedUntil
        if DEBUG : print "current time : %s" % str(currentTime)
        if DEBUG : print "cached util  : %s" % str(cachedUntil)
        
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
                m.accessLvl = oldAccessLvls[m.characterID]
            except:
                continue

        if len(oldMembers) > 0 :
            if len(diffs) > 0 :
                for d in diffs:
                    d.save()
                # we store the update time of the table
                utils.markUpdated(model=MemberDiff, date=currentTime)
            Member.objects.all().delete()
        # to be sure to store the nicknames change, etc.
        # even if there are no diff, we always overwrite the members 
        for m in newMembers.values():
            m.save()
        # we store the update time of the table
        utils.markUpdated(model=Member, date=currentTime)
            
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"

        return "%d members parsed, %d changes since last scan" % (len(newMembers), len(diffs))
    except:
        # mayday, error
        transaction.rollback()
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
    locID    = member["locationID"]
    ship     = member["shipType"]
    
    return Member(characterID=id,    name=name,         nickname=nick,
                  baseID=base,       corpDate=corpDate, lastLogin=login,
                  lastLogoff=logoff, locationID=locID,  ship=ship)
    
#------------------------------------------------------------------------------
def getDiffs(oldMembers, newMembers, date):
    removed, added = utils.calcDiffs(oldItems=oldMembers, newItems=newMembers)
    
    diffs  = []
    
    if DEBUG:
        print "RESIGNED MEMBERS:"
        if not removed : print "(none)"
    for oldmember in removed:
        if DEBUG: print "- %s (%s)" % (oldmember.name, oldmember.nickname)
        diffs.append(MemberDiff(characterID = oldmember.characterID, 
                                name        = oldmember.name,
                                nickname    = oldmember.nickname, 
                                new=False, date=date))
    if DEBUG:
        print "NEW MEMBERS:"
        if not removed : print "(none)"
    for newmember in added:
        if DEBUG: print "+ %s (%s)" % (newmember.name, newmember.nickname)
        diffs.append(MemberDiff(characterID = newmember.characterID, 
                                name        = newmember.name,
                                nickname    = newmember.nickname, 
                                new=True, date=date))
    return diffs, removed
    
