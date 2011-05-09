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

__date__ = "2010-03-18"
__author__ = "diabeteman"

from django.db import models
from datetime import datetime

from ecm.core import evedb
from ecm.lib import bigintpatch

#------------------------------------------------------------------------------
class Asset(models.Model):
    itemID = models.BigIntegerField(primary_key=True) # supposed to be unique
    solarSystemID = models.BigIntegerField()
    stationID = models.BigIntegerField()
    hangarID = models.PositiveIntegerField() # hangar division
    container1 = models.BigIntegerField(null=True, blank=True) # first container or ship
    container2 = models.BigIntegerField(null=True, blank=True) # second container or ship
    typeID = models.PositiveIntegerField(default=0) # item type ID from the EVE database
    quantity = models.BigIntegerField(default=0)
    flag = models.BigIntegerField() # used to determine the state or path of the asset
    singleton = models.BooleanField(default=False) # true if assembled 
    hasContents = models.BooleanField(default=False) # true if item container

    h = None
    
    def __repr__(self):
        return str(self)

    def __str__(self):
        try:
            item = evedb.resolveTypeName(self.typeID)[0]
            return "<%s x%d>" % (item, self.quantity)
        except:
            return "<Asset instance at %x>" % id(self)

    def __hash__(self):
        if self.h is None:
            string = (str(self.solarSystemID) + str(self.stationID) + str(self.hangarID) 
                      + str(self.typeID) + str(self.quantity))
            self.h = hash(string)
        return self.h
        
    def __eq__(self, other):
        return (self.solarSystemID == other.solarSystemID
                and self.stationID == other.stationID 
                and self.hangarID == other.hangarID 
                and self.typeID == other.typeID
                and self.quantity == other.quantity)
    
    def __cmp__(self, other):
        return (cmp(self.solarSystemID, other.solarSystemID)
                or cmp(self.stationID, other.stationID) 
                or cmp(self.hangarID, other.hangarID) 
                or cmp(self.typeID, other.typeID))
    
    def lookslike(self, other):
        """
        This is NOT a real equality, this method is used to find duplicates in diffs
        """
        return (self.solarSystemID == other.solarSystemID
                and self.stationID == other.stationID 
                and self.hangarID == other.hangarID 
                and self.typeID == other.typeID)
    
#------------------------------------------------------------------------------
class AssetDiff(models.Model):
    id = bigintpatch.BigAutoField(primary_key=True)
    solarSystemID = models.BigIntegerField()
    stationID = models.BigIntegerField()
    hangarID = models.PositiveIntegerField() # hangar division
    typeID = models.PositiveIntegerField(default=0) # item type ID from the EVE database
    quantity = models.IntegerField(default=0)
    date = models.DateTimeField(db_index=True, default=datetime.now())
    new = models.BooleanField()
    flag = models.BigIntegerField() # used to determine the state or path of the asset
    

    
    
