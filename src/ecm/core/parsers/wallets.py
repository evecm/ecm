'''
Created on 27 mars 2011

@author: diabeteman
'''


from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from ecm.data.roles.models import TitleComposition, Title, Role, TitleCompoDiff
from ecm.core.api import connection
from ecm.core.parsers import utils
from ecm.core.parsers.utils import checkApiVersion, markUpdated

from ecm import settings

import logging.config
from ecm.data.corp.models import Wallet
from ecm.data.wallets.models import AccountingEntry
from django.db.models.aggregates import Max

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("parser_wallets")

#------------------------------------------------------------------------------
@transaction.commit_manually
def update():
    try:
        for wallet in Wallet.objects.all():
            update_wallet(wallet)
    except Exception, e:
        # error catched, rollback changes
        transaction.rollback()
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        logger.error("".join(errortrace))
        raise



def update_wallet(wallet):
    
    logger.info("fetching /corp/WalletJournal.xml.aspx...")
    # connect to eve API
    api = connection.connect()
    # retrieve /corp/WalletJournal.xml.aspx
    charID = connection.get_api().charID
    
    lastKnownID = AccountingEntry.objects.aggregate(Max("refID")).get("")
    
    
    
    
    
    try:
        walletsApi = api.corp.WalletJournal(characterID=charID, 
                                            accountKey=wallet.walletID, 
                                            fromID=lastKnownID,
                                            rowCount=256)
    except:
        walletsApi = api.corp.WalletJournal(characterID=charID, 
                                            accountKey=wallet.walletID, 
                                            rowCount=256)
    
    checkApiVersion(walletsApi._meta.version)
    
    currentTime = walletsApi._meta.currentTime
    cachedUntil = walletsApi._meta.cachedUntil
    logger.debug("current time : %s", str(currentTime))
    logger.debug("cached util : %s", str(cachedUntil))
    
    logger.debug("parsing api response...")
