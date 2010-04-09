'''
This file is part of ICE Security Management

Created on 9 feb. 2010
@author: diabeteman
'''

import xml.dom.minidom
from xml.dom.minidom import Node

from ISM.parsers.parse_utils import getCurrentTime, checkApiVersion, reachRowset, dateToInt, getNode

from django.db import transaction
from ISM.roles.models import Member, MemberDiff

#------------------------------------------------------------------------------
@transaction.commit_manually
def parse(xmlFile):
    """
    Parses all Member details from an API MemberTracking.xml response.
    Puts all the information into the database.
       
       xmlFile  : can be either a string or a physical file.
       
    """
    doc = xml.dom.minidom.parse(xmlFile)
    checkApiVersion(doc)
    # parse date as a big_integer
    date = getCurrentTime(doc)

    result = getNode(doc, "result")
    members = reachRowset(result, "members")
    newList = []
    
    try:
        # old composition of the titles from the database
        oldList = list(Member.objects.all())

        for member in members.childNodes:
            if not member.nodeType == Node.ELEMENT_NODE:
                continue
            newList.append(parseOneMember(node=member))
        
        if len(oldList) != 0 :
            diffs = getDiffs(newList, oldList, date)
            if diffs :
                for d in diffs: d.save()
                Member.objects.all().delete()
                for c in newList: c.save()
            # if no diff, we do nothing
        else:
            # 1st import
            for c in newList: c.save()
            
        transaction.commit()
    except:
        transaction.rollback()
        raise


#------------------------------------------------------------------------------
def parseOneMember(node):
    
    id       =       int(node.getAttribute("characterID"))
    name     =           node.getAttribute("name")
    nick     =           node.getAttribute("title")
    corpDate = dateToInt(node.getAttribute("startDateTime"))
    base     =       int(node.getAttribute("baseID"))
    login    = dateToInt(node.getAttribute("logonDateTime"))
    logoff   = dateToInt(node.getAttribute("logoffDateTime"))
    locID    =       int(node.getAttribute("locationID"))
    ship     =           node.getAttribute("shipType")
    
    return Member(characterID=id,    name=name,         nickname=nick,
                  baseID=base,       corpDate=corpDate, lastLogin=login,
                  lastLogoff=logoff, locationID=locID,  ship=ship )

    
#------------------------------------------------------------------------------
def getDiffs(newList, oldList, date):
    removed  = [ m for m in oldList if m not in newList ]
    added    = [ m for m in newList if m not in oldList ]
    
    diffs    = []
    for m in removed:
        diffs.append(MemberDiff(characterID=m.characterID, name=m.name,
                                nickname=m.nickname, new=False, date=date))
    for m in added:
        diffs.append(MemberDiff(characterID=m.characterID, name=m.name,
                                nickname=m.nickname, new=True, date=date))
    return diffs
    