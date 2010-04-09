'''
This file is part of ICE Security Management

Created on 11 feb. 2010
@author: diabeteman
'''


import xml.dom.minidom
from xml.dom.minidom import Node

from ISM.parsers.parse_utils import getCurrentTime, checkApiVersion, reachRowset, getNode
from ISM.roles.models import TitleMembership, RoleMembership, RoleType, Role, \
                                RoleMemberDiff, TitleMemberDiff

from django.db import transaction

ROLE_TYPES = {}
for t in RoleType.objects.all() :
    ROLE_TYPES[t.typeName] = t.id

ALL_ROLES = {}
for r in Role.objects.all() :
    ALL_ROLES[(r.roleID, r.roleType_id)] = r.id

DATE = 0

#------------------------------------------------------------------------------
@transaction.commit_manually
def parse(xmlFile):
    """
    Parses all Member details from an API MemberTracking.xml response.
    Puts all the information into the database.
       
       xmlFile  : can be either a string or a physical file.
       
    """
    global DATE
    
    doc = xml.dom.minidom.parse(xmlFile)
    checkApiVersion(doc)
    # parse date as a big_integer
    DATE = getCurrentTime(doc)

    result = getNode(doc, "result")
    members = result.getElementsByTagName("member")
    newRoleList = []
    newTitleList = []

    
    try:
        # old data from the database
        oldRoleList = list(RoleMembership.objects.all())
        oldTitleList = list(TitleMembership.objects.all())
        
        for member in members:
            member.charID = int(member.getAttribute("characterID"))
            newRoleList.extend(parseOneMemberRoles(node=member))
            newTitleList.extend(parseOneMemberTitles(node=member))
        
        storeRoleDiffs(oldRoleList, newRoleList)
        storeTitleDiffs(oldTitleList, newTitleList)
            
        transaction.commit()
    except:
        transaction.rollback()
        raise

#------------------------------------------------------------------------------
def parseOneMemberRoles(node):
    roleList = []
    
    for type in ROLE_TYPES.keys() :
        for row in reachRowset(node, type).childNodes :
            if not row.nodeType == Node.ELEMENT_NODE:
                continue
            r_id = ALL_ROLES[(int(row.getAttribute("roleID")), ROLE_TYPES[type])]
            roleList.append(RoleMembership(member_id=node.charID, role_id=r_id))
    
    return roleList
#------------------------------------------------------------------------------
def parseOneMemberTitles(node):
    titleList = []
    
    for row in reachRowset(node, "titles").childNodes :
        if row.nodeType != Node.ELEMENT_NODE :
            continue
        titleID = int(row.getAttribute("titleID"))
        titleList.append(TitleMembership(member_id=node.charID, title_id=titleID))
            
    return titleList
    
#------------------------------------------------------------------------------
def getRoleMemberDiffs(newList, oldList):
    removed  = [ r for r in oldList if r not in newList ]
    added    = [ r for r in newList if r not in oldList ]
    
    diffs    = []
    for r in removed:
        diffs.append(RoleMemberDiff(role_id=r.id, member_id=r.member_id, 
                                                new=False, date=DATE))
    for r in added:
        diffs.append(RoleMemberDiff(role_id=r.id, member_id=r.member_id, 
                                                new=True, date=DATE))
        
    return diffs
    
#------------------------------------------------------------------------------
def getTitleMemberDiffs(newList, oldList):
    removed  = [ t for t in oldList if t not in newList ]
    added    = [ t for t in newList if t not in oldList ]
    
    diffs    = []
    for t in removed:
        diffs.append(TitleMemberDiff(title_id=t.id, member_id=t.member_id, 
                                                new=False, date=DATE))
    for t in added:
        diffs.append(TitleMemberDiff(title_id=t.id, member_id=t.member_id, 
                                                new=True, date=DATE))
        
    return diffs

#------------------------------------------------------------------------------
def storeRoleDiffs(oldList, newList):
    if len(oldList) != 0 :
        diffs = getRoleMemberDiffs(newList, oldList)
        if diffs :
            for d in diffs: d.save()
            RoleMembership.objects.all().delete()
            for rm in newList: rm.save()
        # if no diff, we do nothing
    else:
        # 1st import
        for rm in newList: rm.save()

#------------------------------------------------------------------------------
def storeTitleDiffs(oldList, newList):
    if len(oldList) != 0 :
        diffs = getTitleMemberDiffs(newList, oldList)
        if diffs :
            for d in diffs: d.save()
            TitleMembership.objects.all().delete()
            for tm in newList: tm.save()
        # if no diff, we do nothing
    else:
        # 1st import
        for tm in newList: tm.save()

