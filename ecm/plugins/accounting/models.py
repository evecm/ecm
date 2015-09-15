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
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ecm.lib import bigintpatch
from ecm.apps.corp.models import Wallet
from ecm.apps.eve.models import Type, CelestialObject


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
    at the following url http://api.eve-online.com/corp/WalletJournal.xml.aspx
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

    DATE_FIELD = 'date' # used for garbage collection

    class Meta:
        get_latest_by = 'refID'
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")

    def __unicode__(self):
        return unicode(self.id)

#------------------------------------------------------------------------------
class TransactionEntry(models.Model):
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['date']
        get_latest_by = 'date'
    
    TYPES = {
             0: 'Buy',
             1: 'Sell',
            }
    FOR = {
           0: 'Personal',
           1: 'Corporation',
          }
    id                   = models.BigIntegerField   (primary_key = True) #@ReservedAssignment
    date                 = models.DateTimeField     ()
    quantity             = models.BigIntegerField   (default = 0)
    typeID               = models.IntegerField      (default = 0)
    price                = models.FloatField        (default = 0.0)
    clientID             = models.BigIntegerField   (default = 0)
    clientName           = models.CharField         (max_length = 128)
    stationID            = models.BigIntegerField   (default = 0)
    transactionType      = models.SmallIntegerField (default = 0, choices=TYPES.items())
    transactionFor       = models.SmallIntegerField (default = 0, choices=FOR.items())
    journal              = models.ForeignKey        (JournalEntry, related_name = 'JournalEntry')
    wallet               = models.ForeignKey        (Wallet, db_index=True)
    
    DATE_FIELD = 'date' # used for garbage collection
    
    @property
    def typeName(self):
        item_name = Type.objects.get(typeID = self.typeID).typeName
        return item_name
    
    @property
    def stationName(self):
        station_name = CelestialObject.objects.get(itemID = self.stationID).itemName
        return station_name
    
    def __unicode__(self):
        return unicode(self.id)
#------------------------------------------------------------------------------
class Contract(models.Model):
    """
    Represents a contract that can be fetched from the API
    at the following url http://api.eve-online.com/corp/Contracts.xml.aspx
    
    More info: http://wiki.eve-id.net/APIv2_Char_Contracts_XML
    """
    
    STATUS_KEYS = {
        'Unknown': -1,
        'Outstanding': 1,
        'Deleted': 2,
        'Completed': 3,
        'Failed': 4,
        'CompletedByIssuer': 5,
        'CompletedByContractor': 6,
        'Cancelled': 7,
        'Rejected': 8,
        'Reversed': 9,
        'InProgress': 10,
    }
    STATUS = dict((key, _(name)) for name, key in STATUS_KEYS.iteritems())

    TYPE_KEYS = {
        'Unkown': -1,
        'ItemExchange': 1,
        'Courier': 2,
        'Loan': 3,
        'Auction': 4,
    }
    TYPE = dict((key, _(name)) for name, key in TYPE_KEYS.iteritems())
    
    AVAILABILITY_KEYS = {
        'Unknown': -1,
        'Private': 0,
        'Public': 1,
    }
    AVAILABILITY = dict((key, _(name)) for name, key in AVAILABILITY_KEYS.iteritems())
    
    class Meta:
        verbose_name ='Contract'
        ordering = ['dateIssued']

    def __hash__(self):
        return self.contractID
    
    def __eq__(self, other):
        return (self.contractID == other.contractID)

    def __cmp__(self, other):
        return cmp(self.contractID, other.contractID)
    
    def __repr__(self):
        return str(self.contractID)

    contractID     = models.BigIntegerField(primary_key=True) # Unique ID for this contract.
    issuerID       = models.BigIntegerField() # Character ID who created contract
    issuerCorpID   = models.BigIntegerField() # Corporation ID who created contract
    assigneeID     = models.BigIntegerField() # Character ID to whom the contract was discharged
    acceptorID     = models.BigIntegerField() # Who will accept the contract.
    startStationID = models.BigIntegerField() # for Couriers contract
    endStationID   = models.BigIntegerField() # for Couriers contract
    type           = models.SmallIntegerField(choices=TYPE.items()) #@ReservedAssignment
    status         = models.SmallIntegerField(choices=STATUS.items())
    title          = models.CharField(max_length=255)
    forCorp        = models.BooleanField() # True if the contract was issued on behalf of the issuer's corporation
    availability   = models.SmallIntegerField(choices=AVAILABILITY.items()) # Public or Private
    dateIssued     = models.DateTimeField(null=True, blank=True)
    dateExpired    = models.DateTimeField(null=True, blank=True)
    dateAccepted   = models.DateTimeField(null=True, blank=True)
    dateCompleted  = models.DateTimeField(null=True, blank=True)
    numDays        = models.SmallIntegerField() # Number of days to perform the contract
    price          = models.FloatField() # Price of contract (for ItemsExchange and Auctions)
    reward         = models.FloatField() # Remuneration for contract (for Couriers only)
    collateral     = models.FloatField() # Collateral price (for Couriers only)
    buyout         = models.FloatField() # Buyout price (for Auctions only)
    volume         = models.FloatField() # Volume of items in the contract (courier)
    
    DATE_FIELD = 'dateIssued' # used for garbage collection
    
    @property
    def permalink(self):
        url = '/accounting/contracts/%d/' % self.contractID
        title = "&#35;%s" % self.contractID
        return '<a href="%s" class="contract">%s</a>' % (url, title)
    
    @property
    def permalink_type(self):
        TYPE_LINK = '<img src="%s" alt="%s" name="%s" class="contracttype"/>'
        lower_type = self.get_type_display().lower()
        return TYPE_LINK % ('%saccounting/img/%s.png' % (settings.STATIC_URL, lower_type),
                            self.type, self.type)
    
    @property
    def status_html(self):
        status = Contract.STATUS[self.status]
        return '<span class="contract-%s">%s</span>' % (status.lower(), status)
    
    def availability_string(self):
        return unicode(Contract.AVAILABILITY[self.availability])
        
    def status_string(self):
        return unicode(Contract.STATUS[self.status])
        
#------------------------------------------------------------------------------
class ContractItem(models.Model):
    """
    Represents a contract item that can be fetched from the API
    at the following url http://api.eve-online.com/corp/ContractItems.xml.aspx
    """
    class Meta:
        verbose_name = 'Contract Item'

    def __hash__(self):
        return self.recordID
    
    def __eq__(self, other):
        return (self.recordID == other.recordID)

    def __cmp__(self, other):
        return cmp(self.recordID, other.recordID)

    contract    = models.ForeignKey(Contract, related_name='items')
    recordID    = models.BigIntegerField()
    typeID      = models.IntegerField()
    quantity    = models.BigIntegerField()
    rawQuantity = models.BigIntegerField()
    singleton   = models.SmallIntegerField()
    included    = models.SmallIntegerField()

#------------------------------------------------------------------------------
class MarketOrder(models.Model):
    """
    Represents a contract item that can be fetched from the API
    at the following url http://api.eve-online.com/corp/MarketOrders.xml.aspx
    """
    class Meta:
        verbose_name = 'Market Order'
        ordering     = ['orderID']

    STATE = {
        0: 'Open/Active', 
        1: 'Closed', 
        2: 'Expired (or Fulfilled)', 
        3: 'Cancelled', 
        4: 'Pending', 
        5: 'Character Deleted',
    }

    def __hash__(self):
        return self.orderID

    orderID      = models.BigIntegerField(primary_key=True)
    charID       = models.BigIntegerField()
    stationID    = models.BigIntegerField()
    volEntered   = models.BigIntegerField()
    volRemaining = models.BigIntegerField()
    minVolume    = models.BigIntegerField()
    orderState   = models.SmallIntegerField(choices=STATE.items())
    typeID       = models.IntegerField()
    range        = models.SmallIntegerField() #@ReservedAssignment
    accountKey   = models.ForeignKey(Wallet, related_name='market_orders')
    duration     = models.SmallIntegerField()
    escrow       = models.FloatField()
    price        = models.FloatField()
    bid          = models.BooleanField(default=False)
    issued       = models.DateTimeField()

    DATE_FIELD = 'issued' # used for garbage collection

    @property
    def get_type(self):
        if self.bid:
            return 'Buy Order'
        else:
            return 'Sell Order'
        
    STATE_CSS = {
        0: 'inprogress',
        1: 'completed',
        2: 'completed',
        3: 'cancelled',
        4: 'inprogress',
        5: 'deleted',
    }
    @property
    def state_html(self):
        css_class = MarketOrder.STATE_CSS[self.orderState]
        state_text = MarketOrder.STATE[self.orderState]
        return '<span class="contract-%s">%s</span>' % (css_class, state_text)
    
    @property
    def map_range(self):
        _range_map = {-1: 'Station', 32767: 'Region'}
        # check if it is a buy order
        if self.bid:
            return _range_map.get(int(self.range), '%d Jumps' % self.range)
        else:
            # Sell orders are bound to station
            return _range_map.get(-1)
#------------------------------------------------------------------------------
class Report(models.Model):
    """
    A customizable Report for wallet entries.
    """
    class Meta:
        verbose_name = 'Report'
    
    name = models.CharField(max_length=255) # name of this report
    entry_types = models.ManyToManyField(EntryType) # wallet entry types to use for this report
    default_period = models.IntegerField(null=True, blank=True) # the default period for this report
    default_step= models.IntegerField(null=True, blank=True) # the default step in days for this report
