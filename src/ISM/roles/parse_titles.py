"""
This file is part of ICE Security Management

Created on 24 jan. 2010
@author: diabeteman
"""

import xml.dom.minidom
from xml.dom.minidom import Node

from ISM.roles.models import Role, Title, RoleType, TitleComposition, TitleCompoDiff
from ISM.roles import parse_utils
from ISM.exceptions import MalformedXmlResponse, DatabaseCorrupted

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction

#______________________________________________________________________________
@transaction.commit_manually
def parse(xmlFile):
    """
    Parses all Corporation Titles from an API Titles.xml response.
    Puts all the information into the database.
       
       xmlFile  : can be either a string or a physical file.
       
    """
    try:
        doc = xml.dom.minidom.parse(xmlFile)
        parse_utils.checkApiVersion(doc)
    
        # parse date
        date = parse_utils.getCurrentTime(doc)
    
        # parse titles
        titles = parse_utils.reachResult(doc, "titles")
    
   
        newList = []
        oldList = list(TitleComposition.objects.all())
        
        for title in titles.childNodes:
            if not title.nodeType == Node.ELEMENT_NODE:
                continue
            newList.extend(parseOneTitle(node=title))
        
        diffs = getDiffs(newList, oldList, date)
        
        for d in diffs: d.save()
        TitleComposition.objects.all().delete()
        for c in newList: c.save()
            
        transaction.commit()
    except:
        transaction.rollback()
        raise

#______________________________________________________________________________
def parseOneTitle(node):
    roleList = []
    
    # retrieve title name and change it if different. The change will not be
    # logged in the database as we dont really care about that...
    t_id = node.getAttribute("titleID")
    t_name = node.getAttribute("titleName")
    if not t_id or not t_name:
        raise MalformedXmlResponse
    try:
        title = Title.objects.get(titleID=t_id)
        if not title.titleName == t_name:
            title.titleName = t_name
            title.save()
    except MultipleObjectsReturned:
        raise DatabaseCorrupted
    except ObjectDoesNotExist:
        title = Title.objects.create(titleID=t_id, titleName=t_name)

    for categ in node.childNodes:
        if not categ.nodeType == Node.ELEMENT_NODE:
            continue
        roleList.extend(parseCateg(node=categ, title=title))
        
    return roleList
            
#______________________________________________________________________________
def parseCateg(node, title):
    c_name = node.getAttribute("name")
    
    subList = []
    
    try:
        categ = RoleType.objects.get(typeName=c_name)
    except ObjectDoesNotExist:
        raise MalformedXmlResponse, "roleType: %s does not exist" % c_name

    for role_node in node.childNodes:
        if not role_node.nodeType == Node.ELEMENT_NODE:
            continue
        r_id = role_node.getAttribute("roleID")
        
        try:
            aRole = Role.objects.get(roleID=r_id, roleType=categ)
        except ObjectDoesNotExist:
            raise MalformedXmlResponse, "role with id=%s does not exist" % r_id
        
        subList.append(TitleComposition(title=title, role=aRole))
        
    return subList

#______________________________________________________________________________
def getDiffs(newList, oldList, date):
    removed  = [ c for c in oldList if c not in newList ]
    added    = [ c for c in newList if c not in oldList ]
    diffs    = []
    
    for c in removed:
        diffs.append(TitleCompoDiff(isNew=False, date=date, title=c.title, role=c.role))
    for c in added:
        diffs.append(TitleCompoDiff(isNew=True, date=date, title=c.title, role=c.role))
        
    return diffs
    