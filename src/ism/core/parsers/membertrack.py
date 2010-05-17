'''
This file is part of ICE Security Management

Created on 9 feb. 2010
@author: diabeteman
'''
from django.db import transaction
from ism.data.roles.models import Member, MemberDiff
from ism.core.api import connection
from ism.core.api.connection import API
from ism.core.parsers.utils import checkApiVersion, markUpdated
from datetime import datetime

DEBUG = False # DEBUG mode

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(debug=False):
    """
    Retrieve all corp members, with all basic information about them.
    If some members have left or have arrived we also store the diff in the database.
    
    If there's an error, nothing is written in the database
    """
    global DEBUG
    DEBUG = debug
    
    try:
        # connect to eve API
        api = connection.connect(debug=debug)
        # retrieve /corp/MemberTracking.xml.aspx
        membersApi = api.corp.MemberTracking(characterID=API.CHAR_ID)
        checkApiVersion(membersApi._meta.version)
        
        currentTime = membersApi._meta.currentTime
        cachedUntil = membersApi._meta.cachedUntil
        if DEBUG : print "current time : %s" % str(datetime.fromtimestamp(currentTime))
        if DEBUG : print "cached util  : %s" % str(datetime.fromtimestamp(cachedUntil))
        
        newList = []
        
        # we get the old member list from the database
        oldList = list(Member.objects.all())

        for member in membersApi.members:
            newList.append(parseOneMember(member=member))
        
        if len(oldList) != 0 :
            diffs = getDiffs(newList, oldList, currentTime)
            if diffs:
                for d in diffs: d.save()
                # we store the update time of the table
                markUpdated(model=MemberDiff, date_int=currentTime)
            Member.objects.all().delete()
            # to be sure to store the nicknames change, etc.
            # even if there are no diff, we always overwrite the members 
        for c in newList: c.save()
        # we store the update time of the table
        markUpdated(model=Member, date_int=currentTime)
            
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"
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
                  lastLogoff=logoff, locationID=locID,  ship=ship )
    
#------------------------------------------------------------------------------
def getDiffs(newList, oldList, date):
    removed  = [ r for r in oldList if r not in newList ]
    added    = [ a for a in newList if a not in oldList ]
    
    diffs    = []
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
    return diffs
    