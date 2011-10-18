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


import logging
from datetime import datetime

from django.db import transaction

from ecm.core.eve import api

from ecm.apps.corp.models import Wallet
from ecm.core.parsers import markUpdated, checkApiVersion
from ecm.plugins.accounting.parsers import fix_encoding
from ecm.plugins.accounting.models import JournalEntry

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update():
    """
    Updates all wallets with the missing accounting entries since last scan.
    """
    try:
        for wallet in Wallet.objects.all():
            update_wallet(wallet)

        markUpdated(model=JournalEntry, date=datetime.now())
        LOG.debug("wallets journal updated")
    except:
        # error catched, rollback changes
        LOG.exception("update failed")
        raise

#------------------------------------------------------------------------------
def update_wallet(wallet):
    try:
        lastKnownID = JournalEntry.objects.filter(wallet=wallet).latest().refID
    except JournalEntry.DoesNotExist:
        lastKnownID = 0
    entries = fetch_entries(wallet, lastKnownID)

    LOG.debug("parsing results...")
    for e in entries:
        if e.reason.startswith('DESC:'):
            # the "reason" field encoding is bugged
            # we must fix all special characters
            # see 'fix_encoding()'
            e.reason = e.reason[len('DESC: '):]
            e.reason = fix_encoding(e.reason).strip('\'" \t\n')
            e.reason = u'DESC: ' + e.reason
        JournalEntry.objects.create(refID=e.refID,
                                    wallet=wallet,
                                    date=e.date,
                                    type_id=e.refTypeID,
                                    ownerName1=e.ownerName1,
                                    ownerID1=e.ownerID1,
                                    ownerName2=e.ownerName2,
                                    ownerID2=e.ownerID2,
                                    argName1=e.argName1,
                                    argID1=e.argID1,
                                    amount=e.amount,
                                    balance=e.balance,
                                    reason=e.reason)
    LOG.info("%d entries added in journal" % len(entries))


def fetch_entries(wallet, lastKnownID):
    api_conn = api.connect()

    LOG.info("fetching /corp/WalletJournal.xml.aspx "
                "(accountKey=%d)..." % wallet.walletID)
    charID = api.get_api().characterID
    walletsApi = api_conn.corp.WalletJournal(characterID=charID,
                                            accountKey=wallet.walletID,
                                            rowCount=256)
    checkApiVersion(walletsApi._meta.version)

    entries = list(walletsApi.entries)
    if len(entries) > 0:
        minID = min([e.refID for e in walletsApi.entries])
    else:
        minID = 0

    # after the first fetch, we perform "journal walking"
    # only if we got 256 entries in the response (meaning more to come)
    # or if the lastKnownID is in the current 256 entries
    # (entries are supposed to be sorted by decreasing refIDs)
    while len(walletsApi.entries) == 256 and minID > lastKnownID:
        LOG.info("fetching /corp/WalletJournal.xml.aspx "
                    "(accountKey=%d, fromID=%d)..." % (wallet.walletID, minID))
        walletsApi = api_conn.corp.WalletJournal(characterID=charID,
                                                 accountKey=wallet.walletID,
                                                 fromID=minID,
                                                 rowCount=256)
        checkApiVersion(walletsApi._meta.version)
        entries.extend(list(walletsApi.entries))
        if len(walletsApi.entries) > 0:
            minID = min([e.refID for e in walletsApi.entries])

    # we sort the entries by increasing refIDs in order to remove
    # the ones we already have in the database
    entries.sort(key=lambda e: e.refID)

    while len(entries) != 0 and entries[0].refID <= lastKnownID:
        # we already have this entry, no need to keep it
        del entries[0]

    return entries
