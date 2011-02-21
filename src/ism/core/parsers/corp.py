'''
This file is part of ICE Security Management

Created on 8 feb. 2010
@author: diabeteman
'''
from ism.data.corp.models import Corp, Hangar, Wallet
from ism.core.api import connection
from ism.core.api.connection import API

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from ism.core.parsers.utils import checkApiVersion, markUpdated

from ism import settings

import logging.config

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("parser_corp")

#------------------------------------------------------------------------------
@transaction.commit_manually
def update(cache=False):
    """
    Fetch a /corp/CorporationSheet.xml.aspx api response, parse it and store it to 
    the database.
    """
    
    try:
        logger.info("fetching /corp/CorporationSheet.xml.aspx...")
        # connect to eve API
        api = connection.connect(cache=cache)
        # retrieve /corp/CorporationSheet.xml.aspx
        corpApi = api.corp.CorporationSheet(characterID=API.CHAR_ID)
        checkApiVersion(corpApi._meta.version)

        currentTime = corpApi._meta.currentTime
        cachedUntil = corpApi._meta.cachedUntil
        logger.debug("current time : %s", str(currentTime))
        logger.debug("cached util : %s", str(cachedUntil))

        logger.debug("parsing api response...")
        try: 
            allianceName = corpApi.allianceName
            allianceID   = corpApi.allianceID
            allianceTicker = ""
            alliancesApi = api.eve.AllianceList()
            for a in alliancesApi.alliances:
                if a.allianceID == allianceID:
                    allianceTicker = a.shortName
                    break
        except:
            allianceName = "-"
            allianceID   = 0
            allianceTicker = "-"

        try:
            # try to retrieve the db stored corp info
            corp = Corp.objects.get(id=1)
            corporationID=corpApi.corporationID
            corp.corporationName = corpApi.corporationName
            corp.ticker          = corpApi.ticker
            corp.ceoID           = corpApi.ceoID
            corp.ceoName         = corpApi.ceoName
            corp.stationID       = corpApi.stationID
            corp.stationName     = corpApi.stationName
            corp.allianceID      = allianceID
            corp.allianceName    = allianceName
            corp.allianceTicker  = allianceTicker
            corp.description     = corpApi.description
            corp.taxRate         = corpApi.taxRate
            corp.memberLimit     = corpApi.memberLimit

        except ObjectDoesNotExist:
            # no corp parsed yet
            corp = Corp( id              = 1,
                         corporationID   = corpApi.corporationID, 
                         corporationName = corpApi.corporationName,
                         ticker          = corpApi.ticker,      
                         ceoID           = corpApi.ceoID,
                         ceoName         = corpApi.ceoName,
                         stationID       = corpApi.stationID,     
                         stationName     = corpApi.stationName,     
                         description     = corpApi.description,
                         allianceID      = allianceID,
                         allianceName    = allianceName,
                         allianceTicker  = allianceTicker,
                         taxRate         = corpApi.taxRate,      
                         memberLimit     = corpApi.memberLimit )
        
        corp.save()
        
        # we store the update time of the table
        markUpdated(model=Corp, date=currentTime)
        
        logger.debug("name: %s [%s]", corp.corporationName, corp.ticker)
        logger.debug("alliance: %s <%s>", corp.allianceName, corp.allianceTicker)
        logger.debug("CEO: %s", corpApi.ceoName)
        logger.debug("tax rate: %d%%", corp.taxRate)
        logger.debug("member limit: %d", corp.memberLimit)
            
        logger.debug("HANGAR DIVISIONS:")
        for hangarDiv in corpApi.divisions :
            h_id   = hangarDiv.accountKey
            h_name = hangarDiv.description
            try:
                h = Hangar.objects.get(hangarID=h_id)
            except ObjectDoesNotExist:
                h = Hangar(hangarID=h_id, name=h_name)
            logger.debug("  %s [%d]", h.name, h.hangarID)
            h.save()
        
        # we store the update time of the table
        markUpdated(model=Hangar, date=currentTime)
        
        logger.debug("WALLET DIVISIONS:")
        for walletDiv in corpApi.walletDivisions :
            w_id   = walletDiv.accountKey
            w_name = walletDiv.description
            try:
                w = Wallet.objects.get(walletID=w_id)
            except ObjectDoesNotExist:
                w = Wallet(walletID=w_id, name=w_name)
            logger.debug("  %s [%d]", w.name, w.walletID)
            w.save()
        
        # we store the update time of the table
        markUpdated(model=Wallet, date=currentTime)
        
        # all ok
        logger.debug("saving data to the database...")
        transaction.commit()
        logger.debug("DATABASE UPDATED!")
        logger.info("corp info updated")
    except Exception, e:
        # error catched, rollback changes
        transaction.rollback()
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        logger.error("".join(errortrace))
        raise
