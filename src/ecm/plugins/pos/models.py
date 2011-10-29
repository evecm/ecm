# Copyright (c) 2010-2011 Jerome Vacher
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

__date__ = "2011 04 23"
__author__ = "JerryKhan"

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
#JVA from ecm.core.cache import cached_property

FUELCOMPOS = { #XXX TO DELETE (deja fait dans les commons)
      44:'enrichedUranium'
    , 3683:'oxygen'
    , 3689:'mechanicalParts'
    , 9832:'coolant'
    , 9848:'robotics'
    , 16273:'liquidOzone'
    , 16272:'heavyWater'
    , 17887:'oxygenIsotopes'
    , 17888:'nitrogenIsotopes'
    , 17889:'hydrogenIsotopes'
    , 16274:'heliumIsotopes'
    , 16275:'strontiumClathrates'
   }

# Building of the reverse table to address images and so on from fields.
FUELID = {}
for k,v in FUELCOMPOS.items(): FUELID[v] = k


#------------------------------------------------------------------------------
class POS(models.Model):
    
    State_texts = ['Unanchorded','Anchored/Offline','Onlining','Reinforced','Online']
    
    itemID          = models.BigIntegerField(primary_key=True) # supposed to be unique
    locationID      = models.BigIntegerField(db_index=True) # ID of the station
    location        = models.CharField(max_length=256, default="???") # the complete name of the system
    moonID          = models.BigIntegerField() # Moon ID of the POS. how to build it ? 
    mlocation       = models.CharField(max_length=256, default="???")
    typeID          = models.IntegerField() # item type ID from the EVE database: 16213:calda, 16214:minmat, 12236:gal, 27535:Dread Gu, 27538:Shadow
                                            # select * from invTypes where marketGroupID=="478" All control tower available on the market (empire ones)
                                            # select * from invTypes where typeID=="27538"   The shadow control tower only
                                            # select * from invTypes where categoryID=="23"  All tower anchored objects
                                            # select * from invTypes where groupID=="365"   All control towers
    state           = models.IntegerField() # State of the POS : 0:Unanchored,1:Anchored / Offline,2:Onlining,3:Reinforced,4:Online
    stateTimestamp  = models.DateTimeField() # date of the state (important to know when something appends)
    onlineTimestamp = models.DateTimeField() # Online date (important to know when changes occures.)
    cachedUntil     = models.DateTimeField() # Cached date ... il the current cached date is the same, no need to update the database (concerns only starbase details) 
    standingOwnerID = models.BigIntegerField() # Standing ... 
    typeName        = models.CharField(max_length=256, default="???") # to put the type name of the POS.
    isotope         = models.CharField(max_length=256, default="???") # To put the isotop type for this POS.
    #size                    = models.SmallIntegerField() # 1:small, 2:medium, 3: large (try to get it from EVEDB...
    usageFlags              = models.SmallIntegerField()
    deployFlags             = models.SmallIntegerField()
    onStandingDropStanding  = models.SmallIntegerField()
    
    allowCorporationMembers = models.BooleanField(default=False)
    allowAllianceMembers    = models.BooleanField(default=False)
    onStatusDropEnabled     = models.BooleanField(default=False)
    onStatusDropStanding    = models.BooleanField(default=False)
    onAggressionEnabled     = models.BooleanField(default=False)
    onCorporationWarEnabled = models.BooleanField(default=False)
    
    customName = models.CharField(max_length=256, null=True, blank=True) # The name the user is a le to set by himself to give a specific name to the station
    notes = models.TextField(null=True, blank=True) # A note the user can update for any reasons (comments etc ... )
    
    lastUpdate           = models.DateTimeField(auto_now=True)
    operators             = models.ManyToManyField(User, related_name="operated_poses")
    
    #JVA @cached_property
    def stateText(self):
        return POS.State_texts[self.state]
    
    def Lk2Detail(self):
        return '<a href="/pos/%d" class="pos">%s</a>' % (self.itemID, self.mlocation)
    

        
class FuelLevel(models.Model):
    
    class Meta:
        get_latest_by='date'
        ordering=['pos','typeID','date']
    
    pos = models.ForeignKey(POS, related_name='fuel_levels')
    typeID = models.IntegerField()
    quantity = models.IntegerField()
    date = models.DateTimeField(db_index=True, auto_now_add=True)
    
class FuelConsumption(models.Model):
    class Meta:
        ordering=['pos','typeID']
    
    pos = models.ForeignKey(POS, related_name='fuel_consumptions')
    typeID = models.IntegerField()              # id of fuel type
    consumption = models.IntegerField(default=0)         # consuption of this fuel type
    stability = models.IntegerField(default=0)           # stability of the estimation.
    probableConsumption = models.IntegerField(default=0) # Most often this consumption
    probableStability = models.IntegerField(default=0)   # nb point to reach to change stability
