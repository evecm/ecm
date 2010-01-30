'''
This file is part of ICE Security Management

Created on 24 janv. 2010
@author: diabeteman
'''

import time
import xml.dom.minidom
from xml.dom.minidom import Node

from ISM.roles.models import Role, Title, RoleType, TitleComposition
from ISM.api.constants import API_VERSION
from ISM.exceptions import WrongApiVersion, MalformedXmlResponse, DatabaseCorrupted

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction

#______________________________________________________________________________
@transaction.commit_manually
def parseTitles(xmlFile):
    """
    Parse all Corporation Titles from an API Titles.xml response.
    Put all the information into the database.
    xmlFile can be either a string or a physical file.
    """
    doc = xml.dom.minidom.parse(xmlFile)
    checkApiVersion(doc)

    # parse cached until date
    parseChachedDate(doc)

    # parse titles
    titles = reachResult(doc, "titles")
    try:
        for title in titles.childNodes:
            if not title.nodeType == Node.ELEMENT_NODE:
                continue
            # retrieve title name and change it if different
            t_id = title.getAttribute("titleID")
            name = title.getAttribute("titleName")
            if not t_id or not name:
                raise MalformedXmlResponse
            try:
                t = Title.objects.get(titleID=t_id)
                if not t.titleName == name:
                    t.titleName = name
                    t.save()
            except MultipleObjectsReturned:
                raise DatabaseCorrupted
            except ObjectDoesNotExist:
                t = Title.objects.create(titleID=t_id, titleName=name)

            compo = TitleComposition.objects.filter(title=t)

            for categ in title.childNodes:
                if not categ.nodeType == Node.ELEMENT_NODE:
                    continue
                c_name = categ.getAttribute("name")

                try:
                    rt = RoleType.objects.get(typeName=c_name)
                except:
                    raise DatabaseCorrupted

                for r in categ.childNodes:
                    if not r.nodeType == Node.ELEMENT_NODE:
                        continue
                    r_id = r.getAttribute("roleID")
                    
                    try:
                        aRole = Role.objects.get(roleID=r_id, roleType=rt)
                    except MultipleObjectsReturned:
                        raise DatabaseCorrupted
                    except ObjectDoesNotExist:
                        raise DatabaseCorrupted
                    
                    try:
                        compo.get(role=aRole)
                    except MultipleObjectsReturned:
                        raise DatabaseCorrupted
                    except ObjectDoesNotExist:
                        TitleComposition.objects.create(title=t, role=aRole)
                            
        transaction.commit()
    except:
        transaction.rollback()

#______________________________________________________________________________
def parseMemberSecurity(xmlFile):
    """
    Parse all characters' roles and titles from an API MemberSecurity.xml response.
    Put all the information into the database.
    xmlFile can be either a string or a physical file.
    """
    pass

#______________________________________________________________________________
def parseMemberTracking(xmlFile):
    """
    Parse all members' details from an API MemberTracking.xml response.
    Put all the information into the database.
    xmlFile can be either a string or a physical file.
    """
    pass
    
#______________________________________________________________________________
def parseChachedDate(doc):
    """
    Retrieve the cachedUntil date from the document
    """
    cachedUntil = doc.getElementsByTagName("cachedUntil")[0]

    dateString = ""

    for n in cachedUntil.childNodes:
        if n.nodeType == Node.TEXT_NODE:
            dateString += n.nodeValue
    return time.mktime(time.strptime(dateString, '%Y-%m-%d %H:%M:%S'))

#______________________________________________________________________________
def checkApiVersion(doc):
    """
    Check if the API version matches
    """
    api = doc.getElementsByTagName("eveapi")
    if api.length == 1:
        api = api.item(0)
        version = api.getAttribute("version")
        if version == API_VERSION:
            return True
        else:
            raise WrongApiVersion
    else:
        raise MalformedXmlResponse

#______________________________________________________________________________
def reachResult(doc, name):
    titles = doc.getElementsByTagName("result")
    if titles.length == 1:
        titles = titles.item(0)
        for n in titles.getElementsByTagName("rowset"):
            if n.getAttribute("name") == name:
                return n
        raise MalformedXmlResponse
    else:
        raise MalformedXmlResponse

