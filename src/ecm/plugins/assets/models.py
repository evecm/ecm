# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2010-03-18"
__author__ = "diabeteman"

from django.db import models
from datetime import datetime

from ecm.core.eve import db
from ecm.lib import bigintpatch

#------------------------------------------------------------------------------
class Asset(models.Model):
    itemID = models.BigIntegerField(primary_key=True) # supposed to be unique
    solarSystemID = models.BigIntegerField()
    stationID = models.BigIntegerField()
    hangarID = models.PositiveIntegerField() # hangar division
    container1 = models.BigIntegerField(null=True, blank=True) # first container or ship
    container2 = models.BigIntegerField(null=True, blank=True) # second container or ship
    typeID = models.PositiveIntegerField(default=0) # item typeID from the EVE database
    quantity = models.BigIntegerField(default=0)
    flag = models.BigIntegerField() # used to determine the state or path of the asset
    singleton = models.BooleanField(default=False) # true if assembled
    hasContents = models.BooleanField(default=False) # true if item container
    volume = models.FloatField(default=0.0)

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        try:
            item, _ = db.get_type_name(self.typeID)
            return u"<%s x%d>" % (item, self.quantity)
        except:
            return u"<Asset instance at %x>" % id(self)

    def __hash__(self):
        return self.itemID

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
    id = bigintpatch.BigAutoField(primary_key=True) #@ReservedAssignment
    solarSystemID = models.BigIntegerField()
    stationID = models.BigIntegerField()
    hangarID = models.PositiveIntegerField() # hangar division
    typeID = models.PositiveIntegerField(default=0) # item typeID from the EVE database
    quantity = models.IntegerField(default=0)
    date = models.DateTimeField(db_index=True, default=datetime.now())
    new = models.BooleanField()
    flag = models.BigIntegerField() # used to determine the state or path of the asset
    volume = models.BigIntegerField(default=0)

    class Meta:
        get_latest_by = 'date'


