'''
This file is part of EVE Corporation Management

Created on 3 juin 2010
@author: diabeteman
'''

from django.db import models

#------------------------------------------------------------------------------
class JournalEntry(models.Model):
    wallet        = models.PositiveSmallIntegerField() # accountKey
    date          = models.DateTimeField()
    refTypeID     = models.PositiveSmallIntegerField() # type of transaction
    
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
