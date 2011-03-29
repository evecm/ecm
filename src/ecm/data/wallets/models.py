'''
This file is part of EVE Corporation Management

Created on 3 juin 2010
@author: diabeteman
'''

from django.db import models
from ecm.data.corp.models import Wallet

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
class AccountingEntry(models.Model):
    # should be the primary_key but I take some precautions with CCP and let this as a normal field
    refID         = models.BigIntegerField()
    
    wallet        = models.ForeignKey(Wallet, db_index=True)
    date          = models.DateTimeField()
    type          = models.ForeignKey(EntryType, db_index=True) # type of transaction
    
    ownerName1    = models.CharField() # first party of the transaction
    ownerID1      = models.BigIntegerField()
    ownerName2    = models.CharField() # second party of the transaction
    ownerID2      = models.BigIntegerField()
    
    argName1      = models.CharField()                 
    argID1        = models.BigIntegerField()
    
    amount        = models.FloatField() # amount of the transaction
    balance       = models.FloatField() # balance of the account after the transaction
    
    reason        = models.CharField() # comment
    taxReceiverID = models.BigIntegerField()
    taxAmount     = models.DecimalField()
