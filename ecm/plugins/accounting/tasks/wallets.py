# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Robin Jarry
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

from django.db import transaction
from django.utils import timezone
import pytz

from ecm.apps.common import api
from ecm.apps.corp.models import Wallet
from ecm.apps.common.models import UpdateDate
from ecm.plugins.accounting.tasks import fix_encoding
from ecm.plugins.accounting.models import JournalEntry, TransactionEntry

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------

def update():
    """
    Updates all wallets with the missing accounting entries since last scan.
    """
# Temporary fix for this new Wallet division (This is the "Mercenary Wallet")
    for wallet in Wallet.objects.exclude(walletID=10000):
        update_journal_wallet(wallet)
#   for wallet in Wallet.objects.all():
        update_transaction_wallet(wallet)

    UpdateDate.mark_updated(model=JournalEntry, date=timezone.now())
    UpdateDate.mark_updated(model=TransactionEntry, date=timezone.now())
    LOG.debug("wallets journal updated")

#------------------------------------------------------------------------------
def update_journal_wallet(wallet):
    try:
        lastKnownID = JournalEntry.objects.filter(wallet=wallet).latest('refID').refID
    except JournalEntry.DoesNotExist:
        lastKnownID = 0
    entries = fetch_journal_entries(wallet, lastKnownID)
    write_journal_results(wallet, entries)

#------------------------------------------------------------------------------
def update_transaction_wallet(wallet):
    try:
        lastKnownID = TransactionEntry.objects.filter(wallet=wallet).latest('id').id
    except TransactionEntry.DoesNotExist:
        lastKnownID = 0
    entries = fetch_transaction_entries(wallet, lastKnownID)
    write_transaction_results(wallet, entries)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def write_journal_results(wallet, entries):
    LOG.debug("Writing results...")
    for e in entries:
        if e.reason.startswith('DESC:'):
            # the "reason" field encoding is bugged
            # we must fix all special characters
            # see 'fix_encoding()'
            e.reason = e.reason[len('DESC: '):]
            e.reason = fix_encoding(e.reason).strip('\'" \t\n')
            e.reason = u'DESC: ' + e.reason
        e.date = timezone.make_aware(e.date, timezone.utc) #make e.date aware, use utc

        JournalEntry.objects.create(refID=e.refID,
                                    wallet=wallet,
                                    date=e.date.replace(tzinfo=pytz.UTC),
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

#------------------------------------------------------------------------------
@transaction.commit_on_success
def write_transaction_results(wallet, entries):
    LOG.debug("Writing results...")
    for e in entries:
        for t in TransactionEntry.TYPES:
            if TransactionEntry.TYPES[t].lower() == e.transactionType.lower():
                transactionType = t
        for f in TransactionEntry.FOR:
            if TransactionEntry.FOR[f].lower() == e.transactionFor.lower():
                transactionFor = f
        try:
            journal = JournalEntry.objects.get(refID = e.journalTransactionID)
        except JournalEntry.DoesNotExist:
            try:
                journal = JournalEntry.objects.get(argName1 = e.transactionID)
            except JournalEntry.DoesNotExist:
                journal = None
        except JournalEntry.MultipleObjectsReturned, err:
                LOG.warning("Duplicate entries for transaction: %s", err)
                journal = None
        #journal is nono for very old entries. can happen at initial import -> drop fhem.
        if journal != None:
            TransactionEntry.objects.create(
                                            id = e.transactionID,
                                            date = e.transactionDateTime.replace(tzinfo=pytz.UTC),
                                            quantity = e.quantity,
                                            typeID = e.typeID,
                                            price = e.price,
                                            clientID = e.clientID,
                                            clientName = e.clientName,
                                            stationID = e.stationID,
                                            transactionType = transactionType,
                                            transactionFor = transactionFor,
                                            journal = journal,
                                            wallet = wallet,
                                            )
    LOG.info("%d entries added in Transactions" % len(entries))


#------------------------------------------------------------------------------
def fetch_journal_entries(wallet, lastKnownID):
    api_conn = api.connect()

    LOG.info("fetching /corp/WalletJournal.xml.aspx "
                "(accountKey=%d)..." % wallet.walletID)
    charID = api.get_charID()

    # In Iceland an empty wallet causes errors....
    try:
        walletsApi = api_conn.corp.WalletJournal(characterID=charID,
                                                 accountKey=wallet.walletID,
                                                 rowCount=256)
        api.check_version(walletsApi._meta.version)

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
            api.check_version(walletsApi._meta.version)
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
    except api.Error, e:
        LOG.warning("API returned: %s. WalletJournal for account key %s might be empty."
                  % (str(e), wallet.walletID))
        return ''

#------------------------------------------------------------------------------
def fetch_transaction_entries(wallet, lastKnownID):
    api_conn = api.connect()

    LOG.info("fetching /corp/WalletTransactions.xml.aspx "
                "(accountKey=%d)..." % wallet.walletID)
    charID = api.get_charID()

    # In Iceland an empty wallet causes errors....
    try:
        walletsApi = api_conn.corp.WalletTransactions(characterID=charID,
                                                      accountKey=wallet.walletID,
                                                      rowCount=256)
        api.check_version(walletsApi._meta.version)

        transactions = list(walletsApi.transactions)
        if len(transactions) > 0:
            minID = min([e.transactionID for e in walletsApi.transactions])
        else:
            minID = 0

        # after the first fetch, we perform "journal walking"
        # only if we got 256 transactions in the response (meaning more to come)
        # or if the lastKnownID is in the current 256 transactions
        # (transactions are supposed to be sorted by decreasing refIDs)
        while len(walletsApi.transactions) == 256 and minID > lastKnownID:
            LOG.info("fetching /corp/WalletTransactions.xml.aspx "
                        "(accountKey=%d, fromID=%d)..." % (wallet.walletID, minID))
            walletsApi = api_conn.corp.WalletTransactions(characterID=charID,
                                                          accountKey=wallet.walletID,
                                                          fromID=minID,
                                                          rowCount=256)
            api.check_version(walletsApi._meta.version)
            transactions.extend(list(walletsApi.transactions))
            if len(walletsApi.transactions) > 0:
                minID = min([e.transactionID for e in walletsApi.transactions])

        # we sort the transactions by increasing refIDs in order to remove
        # the ones we already have in the database
        transactions.sort(key=lambda e: e.transactionID)

        while len(transactions) != 0 and transactions[0].transactionID <= lastKnownID:
            # we already have this entry, no need to keep it
            del transactions[0]

        return transactions
    except api.Error, e:
        LOG.warning("API returned: %s. WalletTransactions for account key %s might be empty."
                  % (str(e), wallet.walletID))
        return ''