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

from ecm.plugins.pos import constants
from ecm.core.eve import db

#------------------------------------------------------------------------------
class POS(models.Model):
    """
    usageFlags
        access restrictions to the POS fuel bay are encoded in this 4 bit field.

        example: if usageFlags == 9 == 0b1001   -->   10    01
                                                     view  take
            0b10 == 2 --> 'Corporation Members' can view
            0b01 == 1 --> 'Starbase Fuel Tech' can take

    deployFlags
        access restrictions to who is able to operate this POS are encoded in this 8 bit field.

        example: if usageFlags == 68 == 0b01000100  -->   01       00       01      00
                                                        anchor  unanchor  online  offline
            0b01 == 1 --> 'Starbase Fuel Tech' can anchor
            0b00 == 0 --> 'Starbase Config' can unanchor
            0b01 == 1 --> 'Starbase Fuel Tech' can online
            0b00 == 0 --> 'Starbase Config' can offline
    """

    class Meta:
        verbose_name = "POS"
        verbose_name_plural = "POSes"

    STATES = {
        0: 'Unanchorded',
        1: 'Anchored/Offline',
        2: 'Onlining',
        3: 'Reinforced',
        4: 'Online',
    }

    ISOTOPES = {
        constants.OXYGEN_ISOTOPES_TYPEID: 'Oxygen Isotopes',
        constants.HYDROGEN_ISOTOPES_TYPEID: 'Hydrogen Isotopes',
        constants.NITROGEN_ISOTOPES_TYPEID: 'Nitrogen Isotopes',
        constants.HELIUM_ISOTOPES_TYPEID: 'Helium Isotopes',
    }

    # access restrictions are encoded on 2 bits
    ACCESS_RESTRICTIONS = {
        0: '<a href="/hr/roles/roles/9007199254740992/" class="role">Starbase Config</a>',
        1: '<a href="/hr/roles/roles/288230376151711744/" class="role">Starbase Fuel Tech</a>',
        2: 'Corporation Members',
        3: 'Alliance Members',
    }

    ACCESS_MASK = 3

    itemID = models.BigIntegerField(primary_key=True)

    locationID = models.BigIntegerField(default=0)
    location = models.CharField(max_length=255, default="")
    moonID = models.BigIntegerField(default=0)
    moon = models.CharField(max_length=255, default="")
    typeID = models.IntegerField(default=0)
    typeName = models.CharField(max_length=255, default="")

    state = models.SmallIntegerField(choices=STATES.items(), default=0)
    stateTimestamp = models.DateTimeField(auto_now_add=True) # used when pos is reinforced
    onlineTimestamp = models.DateTimeField(auto_now_add=True) # online date (only minutes matter here)
    cachedUntil = models.DateTimeField(auto_now_add=True)

    # general settings
    usageFlags = models.SmallIntegerField(default=0) # see docstring
    deployFlags = models.SmallIntegerField(default=0) # see docstring
    allowCorporationMembers = models.BooleanField(default=False)
    allowAllianceMembers = models.BooleanField(default=False)

    # combat settings
    useStandingsFrom = models.BigIntegerField(default=0)
    standingThreshold = models.FloatField(default=0.0)
    securityStatusThreshold = models.FloatField(default=0.0)
    attackOnConcordFlag = models.BooleanField(default=False)
    attackOnAggression = models.BooleanField(default=False)
    attackOnCorpWar = models.BooleanField(default=False)

    lastUpdate = models.DateTimeField(auto_now_add=True)
    isotopeTypeID = models.BigIntegerField(choices=ISOTOPES.items(), default=0)
    customName = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    operators = models.ManyToManyField(User, related_name="operated_poses")

    @property
    def stateText(self):
        return POS.STATES[self.state]

    @property
    def url(self):
        return '/pos/%d/' % self.itemID

    @property
    def permalink(self):
        moon, _ = db.resolveLocationName(self.moonID)
        return '<a href="%s" class="pos">%s</a>' % (self.url, moon)

    @property
    def fuelBayViewAccess(self):
        return POS.ACCESS_RESTRICTIONS[(self.usageFlags >> 2) & POS.ACCESS_MASK]

    @property
    def fuelBayTakeAccess(self):
        return POS.ACCESS_RESTRICTIONS[self.usageFlags & POS.ACCESS_MASK]

    @property
    def anchorAccess(self):
        return POS.ACCESS_RESTRICTIONS[(self.deployFlags >> 6) & POS.ACCESS_MASK]

    @property
    def unanchorAccess(self):
        return POS.ACCESS_RESTRICTIONS[(self.deployFlags >> 4) & POS.ACCESS_MASK]

    @property
    def onlineAccess(self):
        return POS.ACCESS_RESTRICTIONS[(self.deployFlags >> 2) & POS.ACCESS_MASK]

    @property
    def offlineAccess(self):
        return POS.ACCESS_RESTRICTIONS[self.deployFlags & POS.ACCESS_MASK]

    def state_admin_display(self):
        return self.get_state_display()
    state_admin_display.short_description = "State"

    def isotopes_admin_display(self):
        return self.get_isotopeTypeID_display()
    isotopes_admin_display.short_description = "Isotopes"

    def __unicode__(self):
        return unicode(self.moon)


#------------------------------------------------------------------------------
class FuelLevel(models.Model):

    class Meta:
        get_latest_by = 'date'
        ordering = ['pos', 'date', 'typeID']

    pos = models.ForeignKey(POS, related_name='fuel_levels')
    date = models.DateTimeField(db_index=True, auto_now_add=True)
    typeID = models.IntegerField(db_index=True)
    quantity = models.IntegerField()

    def fuel_admin_display(self):
        fuelName, _ = db.resolveTypeName(self.typeID)
        return unicode(fuelName)
    fuel_admin_display.short_description = "Fuel"

    def __unicode__(self):
        fuelName, _ = db.resolveTypeName(self.typeID)
        return u'%s: %d x %s' % (unicode(self.pos), self.quantity, fuelName)

#------------------------------------------------------------------------------
class FuelConsumption(models.Model):

    class Meta:
        ordering = ['pos', 'typeID']

    pos = models.ForeignKey(POS, related_name='fuel_consumptions')
    typeID = models.IntegerField() # id of fuel type
    consumption = models.IntegerField(default=0) # consumption of this fuel type
    stability = models.IntegerField(default=0) # stability of the estimation.
    probableConsumption = models.IntegerField(default=0) # Most often this consumption
    probableStability = models.IntegerField(default=0) # nb point to reach to change stability

    def fuel_admin_display(self):
        fuelName, _ = db.resolveTypeName(self.typeID)
        return unicode(fuelName)
    fuel_admin_display.short_description = "Fuel"

    def __unicode__(self):
        fuelName, _ = db.resolveTypeName(self.typeID)
        return u'%s: %s = %d / hour' % (unicode(self.pos), fuelName, self.consumption)
