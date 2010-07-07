'''
This file is part of ICE Security Management

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
    corporationID = models.BigIntegerField(primary_key=True)
    corporationName = models.CharField(max_length=256)
    ticker = models.CharField(max_length=8)
    ceoID = models.BigIntegerField()
    stationID = models.PositiveIntegerField()
    allianceName = models.CharField(max_length=256)
    taxRate = models.PositiveSmallIntegerField()
    memberLimit = models.SmallIntegerField()
    
    def __unicode__(self):
        return self.corporationName
    

