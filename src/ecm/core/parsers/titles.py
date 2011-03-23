"""
This file is part of EVE Corporation Management

Created on 24 jan. 2010
@author: diabeteman
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from ecm.data.roles.models import TitleComposition, Title, Role, TitleCompoDiff
from ecm.core.api import connection
from ecm.core.parsers import utils
from ecm.core.parsers.utils import checkApiVersion, markUpdated

from ecm import settings

import logging.config

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("parser_titles")

#------------------------------------------------------------------------------
@transaction.commit_manually
def update():
    """
    Retrieve all corp titles, their names and their role composition.
    If there are changes in the composition of the titles, 
    the changes are also stored in the database.
    
    If there's an error, nothing is written in the database
    """
    try:
        logger.info("fetching /corp/Titles.xml.aspx...")
        # connect to eve API
        api = connection.connect()
        # retrieve /corp/Titles.xml.aspx
        titlesApi = api.corp.Titles(characterID=connection.get_api().charID)
        checkApiVersion(titlesApi._meta.version)
        
        currentTime = titlesApi._meta.currentTime
        cachedUntil = titlesApi._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))
        
        logger.debug("parsing api response...")
        
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
            
        logger.info("%d roles in titles parsed, %d changes since last scan", len(newList), len(diffs))
        transaction.commit()
        logger.debug("DATABASE UPDATED!")
        logger.info("titles updated")
    except Exception, e:
        # error catched, rollback changes
        transaction.rollback()
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        logger.error("".join(errortrace))
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
            raise ValueError("role with id=%s does not exist" % r_id)
        
        # we create a new TitleComposition for the current title
        subList.append(TitleComposition(title=title, role=role))
        
    return subList

#------------------------------------------------------------------------------
def getDiffs(newList, oldList, date):
    removed  = [ r for r in oldList if r not in newList ]
    added    = [ a for a in newList if a not in oldList ]
    diffs    = []
    
    logger.debug("REMOVED ROLES TO TITLES:")
    if not removed : logger.debug("(none)")
    for oldcompo in removed:
        logger.debug("- %s", unicode(oldcompo))
        diffs.append(TitleCompoDiff(title = oldcompo.title, 
                                    role  = oldcompo.role,
                                    new=False, date=date))
    logger.debug("ADDED ROLES TO TITLES:")
    if not removed : logger.debug("(none)")
    for newcompo in added:
        logger.debug("+ %s", unicode(newcompo))
        diffs.append(TitleCompoDiff(title = newcompo.title, 
                                    role  = newcompo.role,
                                    new=True, date=date))
        
    return diffs
    
