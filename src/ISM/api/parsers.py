import time
import xml.dom.minidom
from xml.dom.minidom import Node

from ISM.roles.models import Role, Title, RoleType, TitleComposition

from ISM.api.constants import API_VERSION

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

#______________________________________________________________________________
def parseTitles(xmlFile):
    """
    Parse all Corporation Titles from an API Titles.xml response.
    xmlFile can be either a string or a physical file.
    """
    doc = xml.dom.minidom.parse(xmlFile)

    # parse cached until date
    cachedDate = parseChachedDate(doc)

    # parse titles
    titles = reachTitles(doc)

    for t in titles.childNodes:
        if t.nodeType == Node.ELEMENT_NODE:
            handleTitle(t)

#______________________________________________________________________________
def handleTitle(title):
    """
    Generate a title object from an XML node.
    """
    id = title.getAttribute("titleID")
    name = title.getAttribute("titleName")
    if id and name:
        try:
            t = Title.objects.get(titleID=id)
            if not t.titleName == name:
                t.titleName = name
                t.save()
        except ObjectDoesNotExist:
            t = Title.objects.create(titleID=id, titleName=name)

        compo = TitleComposition.objects.filter(title=t)

        for c in title.childNodes:
            if c.nodeType == Node.ELEMENT_NODE:
                c_name = c.getAttribute("name")

                try:
                    rt = RoleType.objects.get(typeName=c_name)
                except MultipleObjectsReturned:
                    raise
                except ObjectDoesNotExist:
                    rt = RoleType.objects.create(typeName=c_name)

                for r in c.childNodes:
                    if r.nodeType == Node.ELEMENT_NODE:
                        r_id = r.getAttribute("roleID")
                        try:
                            aRole = Role.objects.get(roleID=r_id, roleType=rt)
                        except MultipleObjectsReturned:
                            raise
                        except ObjectDoesNotExist:
                            raise
                        try:
                            compo.get(role=aRole)
                        except MultipleObjectsReturned:
                            raise
                        except ObjectDoesNotExist:
                            TitleComposition.objects.create(title=t, role=aRole)
    else:
        raise AttributeError


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
        raise AttributeError
    version = api.getAttribute("version")
    if version == API_VERSION:
        return True
    else:
        return False

#______________________________________________________________________________
def reachTitles(doc):
    titles = doc.getElementsByTagName("result")
    if titles.length == 1:
        titles = titles.item(0)
    else:
        raise AttributeError

    for n in titles.getElementsByTagName("rowset"):
        if n.getAttribute("name") == "titles":
            return n
