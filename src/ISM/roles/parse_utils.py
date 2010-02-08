"""
This file is part of ICE Security Management

Created on 08 fev. 2010
@author: diabeteman
"""

from ISM.api.constants import API_VERSION
from ISM.exceptions import WrongApiVersion, MalformedXmlResponse

import time
from xml.dom.minidom import Node

#______________________________________________________________________________
def getCachedDate(doc):
    """
    Retrieve the cachedUntil date from a document
    """
    cachedUntil = doc.getElementsByTagName("cachedUntil")[0]

    dateString = ""

    for n in cachedUntil.childNodes:
        if n.nodeType == Node.TEXT_NODE:
            dateString += n.nodeValue
    return time.mktime(time.strptime(dateString, '%Y-%m-%d %H:%M:%S'))

#______________________________________________________________________________
def getCurrentTime(doc):
    """
    Retrieve the cachedUntil date from a document
    """
    cachedUntil = doc.getElementsByTagName("currentTime")[0]

    dateString = ""

    for n in cachedUntil.childNodes:
        if n.nodeType == Node.TEXT_NODE:
            dateString += n.nodeValue
    return dateString

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
    """
    Returns the <result name="?" > node with given name from a document
    """
    titles = doc.getElementsByTagName("result")
    if titles.length == 1:
        titles = titles.item(0)
        for n in titles.getElementsByTagName("rowset"):
            if n.getAttribute("name") == name:
                return n
        raise MalformedXmlResponse
    else:
        raise MalformedXmlResponse
