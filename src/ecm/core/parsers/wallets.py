# Copyright (c) 2010-2011 Robin Jarry
# 
# This file is part of EVE Corporation Management.
# 
# EVE Corporation Management is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or (at your 
# option) any later version.
# 
# EVE Corporation Management is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
# 
# You should have received a copy of the GNU General Public License along with 
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2011-03-27"
__author__ = "diabeteman"




from django.db import transaction
from ecm.core import api
from ecm.core.parsers import utils

import logging
from ecm.data.corp.models import Wallet
from ecm.data.accounting.models import JournalEntry
from django.db.models.aggregates import Max

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_manually
def update():
    """
    Updates all wallets with the missing accounting entries since last scan.
    """
    try:
        for wallet in Wallet.objects.all():
            update_wallet(wallet)
        logger.debug("saving data to the database...")
        transaction.commit()
        logger.debug("update sucessfull")
    except:
        # error catched, rollback changes
        transaction.rollback()
        logger.exception("update failed")


def update_wallet(wallet):
    lastKnownID = JournalEntry.objects.filter(wallet=wallet).aggregate(Max("refID")).get("refID__max")
    if not lastKnownID: lastKnownID = 0
    entries = fetch_entries(wallet, lastKnownID)
    
    logger.debug("parsing results...")
    for e in entries: 
        entry = JournalEntry()
        entry.refID      = e.refID
        entry.wallet     = wallet
        entry.date       = e.date
        entry.type_id    = e.refTypeID
        entry.ownerName1 = e.ownerName1
        entry.ownerID1   = e.ownerID1
        entry.ownerName2 = e.ownerName2
        entry.ownerID2   = e.ownerID2
        entry.argName1   = e.argName1
        entry.argID1     = e.argID1
        entry.amount     = e.amount
        entry.balance    = e.balance
        entry.reason     = e.reason
        entry.save()
    logger.info("%d entries added in journal" % len(entries))


def fetch_entries(wallet, lastKnownID):
    api_conn = api.connect()
    
    logger.info("fetching /corp/WalletJournal.xml.aspx "
                "(accountKey=%d)..." % wallet.walletID)
    charID = api.get_api().charID
    walletsApi = api_conn.corp.WalletJournal(characterID=charID, 
                                            accountKey=wallet.walletID, 
                                            rowCount=256)
    utils.checkApiVersion(walletsApi._meta.version)   
    
    entries = list(walletsApi.entries)
    minID = min([e.refID for e in walletsApi.entries])
    
    # after the first fetch, we perform "journal walking" 
    # only if we got 256 entries in the response (meaning more to come)
    # or if the lastKnownID is in the current 256 entries
    # (entries are supposed to be sorted by decreasing refIDs)
    while len(walletsApi.entries) == 256 and minID > lastKnownID:
        logger.info("fetching /corp/WalletJournal.xml.aspx "
                    "(accountKey=%d, fromID=%d)..." % (wallet.walletID, minID))
        walletsApi = api_conn.corp.WalletJournal(characterID=charID, 
                                                 accountKey=wallet.walletID, 
                                                 fromID=minID,
                                                 rowCount=256)
        utils.checkApiVersion(walletsApi._meta.version)
        entries.extend(list(walletsApi.entries))
        minID = min([e.refID for e in walletsApi.entries])
    
    # we sort the entries by increasing refIDs in order to remove 
    # the ones we already have in the database
    entries.sort(key=lambda e: e.refID)
    
    while len(entries) != 0 and entries[0].refID < lastKnownID:
        # we already have this entry, no need to keep it
        del entries[0]
    
    return entries
