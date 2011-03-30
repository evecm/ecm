"""
The MIT License - EVE Corporation Management

Copyright (c) 2010 Robin Jarry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__date__ = "2011-03-27"
__author__ = "diabeteman"




from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from ecm.data.roles.models import TitleComposition, Title, Role, TitleCompoDiff
from ecm.core import api
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
    

    
    lastKnownID = AccountingEntry.objects.aggregate(Max("refID")).get("refID_max")
    
    
    
    
    
    
    
    logger.debug("parsing api response...")



def fetch_entries(wallet, lastKnownID=None):
    logger.info("fetching /corp/WalletJournal.xml.aspx...")
    # connect to eve API
    api_conn = api.connect()
    # retrieve /corp/WalletJournal.xml.aspx
    charID = api.get_api().charID
    if lastKnownID:
        walletsApi = api_conn.corp.WalletJournal(characterID=charID, 
                                            accountKey=wallet.walletID, 
                                            fromID=lastKnownID,
                                            rowCount=256)
    else:
        walletsApi = api_conn.corp.WalletJournal(characterID=charID, 
                                            accountKey=wallet.walletID, 
                                            rowCount=256)
    
    checkApiVersion(walletsApi._meta.version)   
    currentTime = walletsApi._meta.currentTime
    cachedUntil = walletsApi._meta.cachedUntil
    logger.debug("current time : %s", str(currentTime))
    logger.debug("cached util : %s", str(cachedUntil))
    
