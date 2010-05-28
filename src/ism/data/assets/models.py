'''
This file is part of ICE Security Management

Created on 18 mar. 2010
@author: diabeteman
'''

from django.db import models
from datetime import datetime

#------------------------------------------------------------------------------
class DbAsset(models.Model):
    itemID = models.PositiveIntegerField(primary_key=True) # supposed to be unique
    locationID = models.PositiveIntegerField() # ID of the station
    hangarID = models.PositiveIntegerField() # hangar division
    container1 = models.PositiveIntegerField(null=True, blank=True) # first container or ship
    container2 = models.PositiveIntegerField(null=True, blank=True) # second container or ship
    typeID = models.PositiveIntegerField(default=0) # item type ID from the EVE database
    quantity = models.PositiveIntegerField(default=0)
    flag = models.PositiveIntegerField(default=0) # used to determine the state or path of the asset
    singleton = models.BooleanField(default=False) # true if assembled 
    hasContents = models.BooleanField(default=False) # true if item container

    h = None

    def __hash__(self):
        if not self.h : 
            self.h = self.locationID - self.typeID + self.hangarID * self.quantity
        return self.h

    def __eq__(self, other):
        if self.locationID == other.locationID:
            if self.hangarID == other.hangarID:
                if self.typeID == other.typeID:
                    if self.quantity == other.quantity:
                        return True
                    else: return False
                else: return False
            else: return False
        else: return False
    
    def __cmp__(self, other):
        locdiff = cmp(self.locationID, other.locationID)
        if not locdiff:
            hangardiff = cmp(self.hangarID, other.hangarID)
            if not hangardiff:
                return cmp(self.typeID, other.typeID)
            else:
                return hangardiff
        else:
            return locdiff
    
    def lookslike(self, other):
        """
        This is NOT a real equality, this method is used to find duplicates in diffs
        """
        if self.locationID == other.locationID:
            if self.hangarID == other.hangarID:
                if self.typeID == other.typeID:
                    return True
                else: return False
            else: return False
        else: return False 
#------------------------------------------------------------------------------
class DbAssetDiff(models.Model):
    locationID = models.PositiveIntegerField() # ID of the station
    hangarID = models.PositiveIntegerField() # hangar division
    typeID = models.PositiveIntegerField(default=0) # item type ID from the EVE database
    quantity = models.IntegerField(default=0)
    date = models.DateTimeField(db_index=True, default=datetime.now())
    new = models.BooleanField()
    
#------------------------------------------------------------------------------
class Outpost(models.Model):
    stationID = models.PositiveIntegerField(primary_key=True)
    stationName = models.CharField(max_length=256, default="")
    stationTypeID = models.PositiveIntegerField()
    solarSystemID = models.PositiveIntegerField()
    corporationID = models.PositiveIntegerField()
    corporationName = models.CharField(max_length=256, default="")
    
    def __unicode__(self):
        return self.stationName
    
    
