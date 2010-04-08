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
    container1 = models.IntegerField() # first container or ship
    container2 = models.IntegerField() # second container or ship
    typeID = models.IntegerField() # item ID
    quantity = models.IntegerField()
    flag = models.IntegerField() # used to determine the state or path of the asset
    singleton = models.BooleanField() # true if assembled 
    hasContents = models.BooleanField() # true if item container


