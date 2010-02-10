'''
This file is part of ICE Security Management

Created on 8 feb. 2010
@author: diabeteman
'''

from django.db import models

#______________________________________________________________________________
class Hangar(models.Model):
    hangarID = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

#______________________________________________________________________________
class Wallet(models.Model):
    walletID = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

#______________________________________________________________________________
class Corp(models.Model):
    corporationID = models.IntegerField(primary_key=True)
    corporationName = models.CharField(max_length=256)
    ticker = models.CharField(max_length=8)
    ceoID = models.IntegerField()
    stationID = models.IntegerField()
    allianceName = models.CharField(max_length=256)
    taxRate = models.PositiveSmallIntegerField()
    memberLimit = models.SmallIntegerField()
    
    def __unicode__(self):
        return self.corporationName
    

