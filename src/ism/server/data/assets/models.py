'''
This file is part of ICE Security Management

Created on 18 mar. 2010
@author: diabeteman
'''

from django.db import models

#------------------------------------------------------------------------------
class DbAsset(models.Model):
    itemID = models.IntegerField(primary_key=True) # supposed to be unique
    locationID = models.IntegerField() # ID of the station
    hangarID = models.IntegerField() # hangar division
    container1 = models.IntegerField(null=True, blank=True) # first container or ship
    container2 = models.IntegerField(null=True, blank=True) # second container or ship
    typeID = models.IntegerField(default=0) # item type ID from the EVE database
    quantity = models.IntegerField(default=0)
    flag = models.IntegerField(default=0) # used to determine the state or path of the asset
    singleton = models.BooleanField(default=False) # true if assembled 
    hasContents = models.BooleanField(default=False) # true if item container

    def __repr__(self):
        s = u"%9d %7d %7d %10d"
        return s % (self.locationID, self.hangarID, self.typeID, self.quantity)
    
    def __eq__(self, other):
        return self.locationID == other.locationID\
           and self.hangarID   == other.hangarID\
           and self.typeID     == other.typeID\
           and self.quantity   == other.quantity




class DbAssetDiff(models.Model):
    locationID = models.IntegerField() # ID of the station
    hangarID = models.IntegerField() # hangar division
    typeID = models.IntegerField(default=0) # item type ID from the EVE database
    quantity = models.IntegerField(default=0)
    date = models.IntegerField()
    new = models.BooleanField()
    
    def __repr__(self):
        s = u"%9d %7d %7d %10d"
        return s % (self.locationID, self.hangarID, self.typeID, self.quantity)

        
        
        
        
        
        
        
        