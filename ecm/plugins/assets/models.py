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
from django.utils import timezone

__date__ = "2010-03-18"
__author__ = "diabeteman"

from django.db import models

from ecm.lib import bigintpatch
from ecm.apps.eve.models import Type

#------------------------------------------------------------------------------
class Asset(models.Model):

    class Meta:
        get_latest_by = 'itemID'

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
    
    # added for locating items in solar system
    closest_object_id = models.BigIntegerField(default=0)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    # added for identifying blueprints (True -> Copy, False -> Original, NULL -> not a bp)
    is_bpc = models.NullBooleanField(null=True, blank=True, default=None)
    
    __item = None

    def __repr__(self):
        return str(self)

    def __unicode__(self):
        try:
            return u"<%s x%d>" % (Type.objects.get(pk=self.typeID).typeName, self.quantity)
        except Type.DoesNotExist:
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

    def __getattr__(self, attr):
        try:
            if self.__item is None:
                self.__item = Type.objects.get(pk=self.typeID)
            return getattr(self.__item, attr)
        except AttributeError:
            return models.Model.__getattribute__(self, attr)

#------------------------------------------------------------------------------
class AssetDiff(models.Model):

    class Meta:
        get_latest_by = 'date'

    id = bigintpatch.BigAutoField(primary_key=True) #@ReservedAssignment
    solarSystemID = models.BigIntegerField()
    stationID = models.BigIntegerField()
    hangarID = models.PositiveIntegerField() # hangar division
    typeID = models.PositiveIntegerField(default=0) # item typeID from the EVE database
    quantity = models.IntegerField(default=0)
    date = models.DateTimeField(db_index=True, default=timezone.now())
    new = models.BooleanField()
    flag = models.BigIntegerField() # used to determine the state or path of the asset
    volume = models.BigIntegerField(default=0)

