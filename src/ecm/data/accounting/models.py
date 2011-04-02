# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


__date__ = "2010-06-03"
__author__ = "diabeteman"


from django.db import models
from ecm.data.corp.models import Wallet
from django.utils.translation import ugettext_lazy as _

#------------------------------------------------------------------------------
class EntryType(models.Model):
    """
    Wallet journal entry transaction type
    """
    
    refTypeID = models.PositiveSmallIntegerField(primary_key=True)
    refTypeName = models.CharField(max_length=64)
    
    def __unicode__(self):
        return unicode(self.refTypeName)


#------------------------------------------------------------------------------
class JournalEntry(models.Model):
    """
    Represents a wallet journal entry that can be fetched from the API
    ad the following url http://api.eve-online.com/corp/WalletJournal.xml.aspx
    """
    refID         = models.BigIntegerField() # the couple (refID, wallet_id) should be unique 
    wallet        = models.ForeignKey(Wallet, db_index=True)
    date          = models.DateTimeField()
    type          = models.ForeignKey(EntryType, db_index=True) # type of transaction
    ownerName1    = models.CharField(max_length=128) # first party of the transaction
    ownerID1      = models.BigIntegerField()
    ownerName2    = models.CharField(max_length=128) # second party of the transaction
    ownerID2      = models.BigIntegerField()
    argName1      = models.CharField(max_length=128)                 
    argID1        = models.BigIntegerField()
    amount        = models.FloatField() # amount of the transaction
    balance       = models.FloatField() # balance of the account after the transaction
    reason        = models.CharField(max_length=512) # comment

    class Meta:
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")
