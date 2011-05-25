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

__date__ = "2010-06-03"
__author__ = "diabeteman"


from django.db import models
from ecm.lib import bigintpatch
from ecm.data.corp.models import Wallet
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
    id         = bigintpatch.BigAutoField(primary_key=True)
    refID      = models.BigIntegerField() # the couple (refID, wallet_id) should be unique 
    wallet     = models.ForeignKey(Wallet, db_index=True)
    date       = models.DateTimeField()
    type       = models.ForeignKey(EntryType, db_index=True) # type of transaction
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
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")
