'''
This file is part of EVE Corporation Management

Created on 8 feb. 2010
@author: diabeteman
'''

from django.db import models

#------------------------------------------------------------------------------
class Hangar(models.Model):
    hangarID = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    accessLvl = models.PositiveIntegerField(default=100)

    def __unicode__(self):
        return self.name

#------------------------------------------------------------------------------
class Wallet(models.Model):
    walletID = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    accessLvl = models.PositiveIntegerField(default=100)
    
    def __unicode__(self):
        return self.name

#------------------------------------------------------------------------------
class Corp(models.Model):
    corporationID = models.BigIntegerField()
    corporationName = models.CharField(max_length=256)
    ticker = models.CharField(max_length=8)
    ceoID = models.BigIntegerField()
    ceoName = models.CharField(max_length=256)
    stationID = models.PositiveIntegerField()
    stationName = models.CharField(max_length=256)
    allianceID = models.PositiveIntegerField()
    allianceName = models.CharField(max_length=256)
    allianceTicker = models.CharField(max_length=8)
    description = models.CharField(max_length=2048)
    taxRate = models.PositiveSmallIntegerField()
    memberLimit = models.SmallIntegerField()
    
    def __unicode__(self):
        return self.corporationName
    
    
