"""
This file is part of ICE Security Management

Created on 08 fev. 2010
@author: diabeteman
"""

from ISM.constants import API_VERSION

from ISM.server.logic.exceptions import WrongApiVersion, MalformedXmlResponse

import time
from xml.dom.minidom import Node

#------------------------------------------------------------------------------
def getCachedDate(doc):
    """
    Retrieve the cachedUntil date (as a long integer) from a document
    """
    cachedUntil = getNode(doc, "cachedUntil")

    dateString = getText(cachedUntil)
    return dateToInt(dateString)

#------------------------------------------------------------------------------
def getCurrentTime(doc):
    """
    Retrieve the cachedUntil date (as a long integer) from a document
    """
    currentTime = getNode(doc, "currentTime")

    dateString = getText(currentTime)
    return dateToInt(dateString)

#------------------------------------------------------------------------------
def dateToInt(dateString):
    return time.mktime(time.strptime(dateString, '%Y-%m-%d %H:%M:%S'))

#------------------------------------------------------------------------------
def checkApiVersion(doc):
    """
    Check if the API version matches
    """
    api = getNode(doc, "eveapi")
    
    version = api.getAttribute("version")
    if version == API_VERSION:
        return True
    else:
        raise WrongApiVersion

#------------------------------------------------------------------------------
def reachRowset(node, name):
    """
    Returns the <rowset name="?" > node with given name from a parent node
    """

    for n in node.getElementsByTagName("rowset"):
        if n.getAttribute("name") == name:
            return n
    raise MalformedXmlResponse

#------------------------------------------------------------------------------
def getNode(doc, tagName):
    node = doc.getElementsByTagName(tagName)
    if len(node) == 1:
        return node[0]
    else:
        raise MalformedXmlResponse
#------------------------------------------------------------------------------
def getText(node):
    text = ""
    for n in node.childNodes:
        if n.nodeType == Node.TEXT_NODE:
            text += n.nodeValue
    return text
