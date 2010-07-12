"""
This file is part of ICE Security Management

Created on 24 jan. 2010
@author: diabeteman
"""

from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import transaction
from ism.data.roles.models import TitleComposition, Title, Role, TitleCompoDiff
from ism.core.api import connection
from ism.core.api.connection import API
from ism.core.exceptions import DatabaseCorrupted
from ism.core.parsers import utils
from ism.core.parsers.utils import checkApiVersion, markUpdated

from datetime import datetime

DEBUG = False # DEBUG mode

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(debug=False, cache=False):
    """
    Retrieve all corp titles, their names and their role composition.
    If there are changes in the composition of the titles, 
    the changes are also stored in the database.
    
    If there's an error, nothing is written in the database
    """
    global DEBUG
    DEBUG = debug
    
    try:
        # connect to eve API
        api = connection.connect(debug=debug, cache=cache)
        # retrieve /corp/Titles.xml.aspx
        titlesApi = api.corp.Titles(characterID=API.CHAR_ID)
        checkApiVersion(titlesApi._meta.version)
        
        currentTime = titlesApi._meta.currentTime
        cachedUntil = titlesApi._meta.cachedUntil
        if DEBUG : print "current time : %s" % str(currentTime)
        if DEBUG : print "cached util  : %s" % str(cachedUntil)
        
        newList = []
        # we get all the old TitleComposition from the database
        oldList = list(TitleComposition.objects.all())
        
        for title in titlesApi.titles:
            newList.extend(parseOneTitle(titleApi=title))

        diffs = []
        if len(oldList) != 0 :
            diffs = getDiffs(newList, oldList, currentTime)
            if diffs :
                for d in diffs: d.save()
                # we store the update time of the table
                markUpdated(model=TitleCompoDiff, date=currentTime)
                 
                TitleComposition.objects.all().delete()
                for c in newList: c.save()
                # we store the update time of the table
                markUpdated(model=TitleComposition, date=currentTime)
            # if no diff, we do nothing
        else:
            # 1st import
            for c in newList: c.save()
            # we store the update time of the table
            markUpdated(model=TitleComposition, date=currentTime)
        
        # update titles access levels
        for t in Title.objects.all():
            t.accessLvl = t.getAccessLvl()
            t.save()
            
        transaction.commit()
        if DEBUG: print "DATABASE UPDATED!"

        return "%d roles in titles parsed, %d changes since last scan" % (len(newList), len(diffs))
    except:
        # mayday, error
        transaction.rollback()
        raise

#------------------------------------------------------------------------------
def parseOneTitle(titleApi):
    '''
    Parse all the role for a given title
    
    @param titleApi: one IndexRowset instance from the eveapi module
    @return: a list of TitleComposition objects
    '''
    roleList = []

    id   = titleApi["titleID"]
    name = titleApi["titleName"]
    
    try:
        # retrieval of the title from the database
        title = Title.objects.get(titleID=id)
        if not title.titleName == name:
            # if the titleName has changed, we update it
            title.titleName = name
            title.save()
    except MultipleObjectsReturned:
        raise DatabaseCorrupted
    except ObjectDoesNotExist:
        # the title doesn't exist yet, we create it
        title = Title.objects.create(titleID=id, titleName=name)

    for roleType in utils.roleTypes().values():
        # for each role category, we extend the role composition list for the current title
        roleList.extend(parseRoleType( title    = title, 
                                       roleType = roleType,
                                       roles    = titleApi[roleType.typeName] ))

    return roleList
            
#------------------------------------------------------------------------------
def parseRoleType(title, roleType, roles):
    '''
    Parse all the roles from a category for a given title
    
    @param title:    the current title
    @param roleType: the role category
    @param roles:    all the roles from that category for the given title
    @return: a list of TitleComposition objects
    '''
    
    subList = []
    
    for r in roles:
        r_id = r["roleID"]
        
        try:
            # we get the concerned role
            role = Role.objects.get(roleID=r_id, roleType=roleType.id)
        except ObjectDoesNotExist:
            # if the role does not exist, the database might be corrupted (or API changed?)
            raise DatabaseCorrupted, "role with id=%s does not exist" % r_id
        
        # we create a new TitleComposition for the current title
        subList.append(TitleComposition(title=title, role=role))
        
    return subList

#------------------------------------------------------------------------------
def getDiffs(newList, oldList, date):
    removed  = [ r for r in oldList if r not in newList ]
    added    = [ a for a in newList if a not in oldList ]
    diffs    = []
    
    if DEBUG:
        print "REMOVED ROLES TO TITLES:"
        if not removed : print "(none)"
    for oldcompo in removed:
        if DEBUG: print "- %s" % unicode(oldcompo)
        diffs.append(TitleCompoDiff(title = oldcompo.title, 
                                    role  = oldcompo.role,
                                    new=False, date=date))
    if DEBUG:
        print "ADDED ROLES TO TITLES:"
        if not removed : print "(none)"
    for newcompo in added:
        if DEBUG: print "+ %s" % unicode(newcompo)
        diffs.append(TitleCompoDiff(title = newcompo.title, 
                                    role  = newcompo.role,
                                    new=True, date=date))
        
    return diffs
    
