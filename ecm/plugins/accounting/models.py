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

__date__ = "2010-06-03"
__author__ = "diabeteman"


from django.db import models
from ecm.lib import bigintpatch
from ecm.apps.corp.models import Wallet
from django.utils.translation import ugettext_lazy as _

#------------------------------------------------------------------------------
class EntryType(models.Model):
    """
    Wallet journal entry transaction type
    """
    refTypeID = models.PositiveIntegerField(primary_key=True)
    refTypeName = models.CharField(max_length=64)

    PLAYER_DONATION = 10
    CORP_WITHDRAWAL = 37
    BOUNTY_PRIZES = 85

    def __unicode__(self):
        return unicode(self.refTypeName)


#------------------------------------------------------------------------------
class JournalEntry(models.Model):
    """
    Represents a wallet journal entry that can be fetched from the API
    ad the following url http://api.eve-online.com/corp/WalletJournal.xml.aspx
    """
    id         = bigintpatch.BigAutoField(primary_key=True) #@ReservedAssignment
    refID      = models.BigIntegerField() # the couple (refID, wallet_id) should be unique
    wallet     = models.ForeignKey(Wallet, db_index=True)
    date       = models.DateTimeField()
    type       = models.ForeignKey(EntryType, db_index=True) #@ReservedAssignment
    ownerName1 = models.CharField(max_length=128) # first party of the transaction
    ownerID1   = models.BigIntegerField()
    ownerName2 = models.CharField(max_length=128) # second party of the transaction
    ownerID2   = models.BigIntegerField()
    argName1   = models.CharField(max_length=128)
    argID1     = models.BigIntegerField()
    amount     = models.FloatField() # amount of the transaction
    balance    = models.FloatField() # balance of the account after the transaction
    reason     = models.CharField(max_length=512) # comment

    class Meta:
        get_latest_by = 'refID'
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")

    def __unicode__(self):
        return unicode(self.id)

#------------------------------------------------------------------------------
class Contract(models.Model):
    class Meta:
        verbose_name ='Contract'
        ordering = ['contractID']

    # Unique ID for this contract.
    contractID     = models.PositiveIntegerField()

    # Character ID who created contract
    issuerID       = models.PositiveIntegerField()

    # Corporation ID who created contract
    issuerCorpID   = models.PositiveIntegerField()

    # Character ID to whom the contract was discharged
    assigneeID     = models.PositiveIntegerField()

    # Who will accept the contract. If assigneeID is
    # same as acceptorID then CharacterID else CorporationID
    # (The contract accepted by the corporation)
    acceptorID     = models.PositiveIntegerField()

    # Start station ID (for Couriers contract)
    startStationID = models.PositiveIntegerField()

    # End station ID (for Couriers contract)
    endStationID   = models.PositiveIntegerField()

    # Type of the contract (ItemExchange, Courier, Loan or Auction)
    type           = models.CharField(max_length=255) #@ReservedAssignment

    # Status of the the contract (Outstanding, Deleted, Completed,
    # Failed, CompletedByIssuer, CompletedByContractor, Cancelled,
    # Rejected, Reversed or InProgress)
    status         = models.CharField(max_length=255)

    # Title of the contract
    title          = models.CharField(max_length=255)

    # 1 if the contract was issued on behalf of the issuer's corporation,
    # 0 otherwise
    forCorp        = models.PositiveIntegerField()

    # Public or Private
    availability   = models.CharField(max_length=255)

    # Creation date of the contract
    dateIssued     = models.CharField(max_length=20)

    # Expiration date of the contract
    dateExpired    = models.CharField(max_length=20)

    # Date of confirmation of contract
    dateAccepted   = models.CharField(max_length=20)

    # Number of days to perform the contract
    numDays        = models.PositiveIntegerField()

    # DateTime  Date of completed of contract
    dateCompleted  = models.CharField(max_length=20)

    # Price of contract (for ItemsExchange and Auctions)
    price          = models.FloatField()

    # Remuneration for contract (for Couriers only)
    reward         = models.FloatField()

    # Collateral price (for Couriers only)
    collateral     = models.FloatField()

    # Buyout price (for Auctions only)
    buyout         = models.FloatField()

    # Volume of items in the contract
    volume         = models.FloatField()
