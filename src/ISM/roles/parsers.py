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
    xmlFile can be either a string or a physical file.
    """
    doc = xml.dom.minidom.parse(xmlFile)
    checkApiVersion(doc)

    # parse cached until date
    parseChachedDate(doc)

    # parse titles
    titles = reachTitles(doc)
    try:
        for title in titles.childNodes:
            if title.nodeType == Node.ELEMENT_NODE:
                # retrieve title name and change it if different
                t_id = title.getAttribute("titleID")
                name = title.getAttribute("titleName")
                if t_id and name:
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

                    for c in title.childNodes:
                        if c.nodeType == Node.ELEMENT_NODE:
                            c_name = c.getAttribute("name")

                            try:
                                rt = RoleType.objects.get(typeName=c_name)
                            except:
                                raise DatabaseCorrupted

                            for r in c.childNodes:
                                if r.nodeType == Node.ELEMENT_NODE:
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
                else:
                    raise MalformedXmlResponse
        transaction.commit()
    except:
        transaction.rollback()

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
    else:
        raise MalformedXmlResponse
    version = api.getAttribute("version")
    if version == API_VERSION:
        return True
    else:
        raise WrongApiVersion

#______________________________________________________________________________
def reachTitles(doc):
    titles = doc.getElementsByTagName("result")
    if titles.length == 1:
        titles = titles.item(0)
    else:
        raise MalformedXmlResponse

    for n in titles.getElementsByTagName("rowset"):
        if n.getAttribute("name") == "titles":
            return n
