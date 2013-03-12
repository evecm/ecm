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
from django.core.exceptions import ObjectDoesNotExist

from ecm.lib import bigintpatch, softfk

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
    eve_type = softfk.SoftForeignKey(to='eve.Type')
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
    
    def __unicode__(self):
        try:
            return u'%s x%d' % (self.eve_type.typeName, self.quantity)
        except ObjectDoesNotExist:
            return unicode(id(self))

    def __hash__(self):
        return self.itemID

    def __eq__(self, other):
        return (self.solarSystemID == other.solarSystemID
                and self.stationID == other.stationID
                and self.hangarID == other.hangarID
                and self.eve_type_id == other.eve_type_id
                and self.quantity == other.quantity)

    def __cmp__(self, other):
        return (cmp(self.solarSystemID, other.solarSystemID)
                or cmp(self.stationID, other.stationID)
                or cmp(self.hangarID, other.hangarID)
                or cmp(self.eve_type_id, other.eve_type_id))

    def lookslike(self, other):
        """
        This is NOT a real equality, this method is used to find duplicates in diffs
        """
        return (self.solarSystemID == other.solarSystemID
                and self.stationID == other.stationID
                and self.hangarID == other.hangarID
                and self.eve_type_id == other.eve_type_id)

    def __getattr__(self, attr):
        from ecm.apps.eve.models import Type
        try:
            return Type.__getattr__(self.eve_type, attr) #@UndefinedVariable
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
    eve_type = softfk.SoftForeignKey(to='eve.Type')
    quantity = models.IntegerField(default=0)
    date = models.DateTimeField(db_index=True)
    new = models.BooleanField()
    flag = models.BigIntegerField() # used to determine the state or path of the asset
    volume = models.BigIntegerField(default=0)
    
    DATE_FIELD = 'date' # used for garbage collection
    
    def __unicode__(self):
        try:
            return u'%s x%d' % (self.eve_type.typeName, self.quantity)
        except ObjectDoesNotExist:
            return unicode(id(self))
        
    
    def __getattr__(self, attr):
        from ecm.apps.eve.models import Type
        try:
            return Type.__getattr__(self.eve_type, attr) #@UndefinedVariable
        except AttributeError:
            return models.Model.__getattribute__(self, attr)
