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
    usage_flags
        access restrictions to the POS fuel bay are encoded in this 4 bit field.

        example: if usage_flags == 9 == 0b1001   -->   10    01
                                                      view  take
            0b10 == 2 --> 'Corporation Members' can view
            0b01 == 1 --> 'Starbase Fuel Tech' can take

    deploy_flags
        access restrictions to who is able to operate this POS are encoded in this 8 bit field.

        example: if usage_flags == 68 == 0b01000100  -->   01       00       01      00
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

    FUEL_BLOCKS = {
        constants.CALDARI_FUEL_BLOCK_TYPEID: 'Caldari Fuel Block',
        constants.MINMATAR_FUEL_BLOCK_TYPEID: 'Minmatar Fuel Block',
        constants.AMARR_FUEL_BLOCK_TYPEID: 'Amarr Fuel Block',
        constants.GALLENTE_FUEL_BLOCK_TYPEID: 'Gallente Fuel Block',
    }

    # access restrictions are encoded on 2 bits
    ACCESS_RESTRICTIONS = {
        0: '<a href="/hr/roles/roles/9007199254740992/" class="role">Starbase Config</a>',
        1: '<a href="/hr/roles/roles/288230376151711744/" class="role">Starbase Fuel Tech</a>',
        2: 'Corporation Members',
        3: 'Alliance Members',
    }

    ACCESS_MASK = 3

    item_id = models.BigIntegerField(primary_key=True)

    location_id = models.BigIntegerField(default=0)
    location = models.CharField(max_length=255, default="")
    moon_id = models.BigIntegerField(default=0)
    moon = models.CharField(max_length=255, default="")
    type_id = models.IntegerField(default=0)
    type_name = models.CharField(max_length=255, default="")

    state = models.SmallIntegerField(choices=STATES.items(), default=0)
    state_timestamp = models.DateTimeField(auto_now_add=True) # used when pos is reinforced
    online_timestamp = models.DateTimeField(auto_now_add=True) # online date (only minutes matter here)
    cached_until = models.DateTimeField(auto_now_add=True)

    # general settings
    usage_flags = models.SmallIntegerField(default=0) # see docstring
    deploy_flags = models.SmallIntegerField(default=0) # see docstring
    allow_corporation_members = models.BooleanField(default=False)
    allow_alliance_members = models.BooleanField(default=False)

    # combat settings
    use_standings_from = models.BigIntegerField(default=0)
    standings_threshold = models.FloatField(default=0.0)
    security_status_threshold = models.FloatField(default=0.0)
    attack_on_concord_flag = models.BooleanField(default=False)
    attack_on_aggression = models.BooleanField(default=False)
    attack_on_corp_war = models.BooleanField(default=False)

    fuel_type_id = models.IntegerField(choices=FUEL_BLOCKS.items(), default=0)
    custom_name = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    operators = models.ManyToManyField(User, related_name="operated_poses")
    has_sov = models.BooleanField(default=False)

    @property
    def stateText(self):
        return POS.STATES[self.state]

    @property
    def url(self):
        return '/pos/%d/' % self.item_id

    @property
    def permalink(self):
        moon, _ = db.resolveLocationName(self.moon_id)
        return '<a href="%s" class="pos">%s</a>' % (self.url, moon)

    @property
    def fuel_bay_view_access(self):
        return POS.ACCESS_RESTRICTIONS[(self.usage_flags >> 2) & POS.ACCESS_MASK]

    @property
    def fuel_bay_take_access(self):
        return POS.ACCESS_RESTRICTIONS[self.usage_flags & POS.ACCESS_MASK]

    @property
    def anchor_access(self):
        return POS.ACCESS_RESTRICTIONS[(self.deploy_flags >> 6) & POS.ACCESS_MASK]

    @property
    def unanchor_access(self):
        return POS.ACCESS_RESTRICTIONS[(self.deploy_flags >> 4) & POS.ACCESS_MASK]

    @property
    def online_access(self):
        return POS.ACCESS_RESTRICTIONS[(self.deploy_flags >> 2) & POS.ACCESS_MASK]

    @property
    def offline_access(self):
        return POS.ACCESS_RESTRICTIONS[self.deploy_flags & POS.ACCESS_MASK]

    def state_admin_display(self):
        return self.get_state_display()
    state_admin_display.short_description = "State"

    def isotopes_admin_display(self):
        return self.get_fuel_type_id_display()
    isotopes_admin_display.short_description = "Isotopes"

    def __unicode__(self):
        return unicode(self.moon)


#------------------------------------------------------------------------------
class FuelLevel(models.Model):

    class Meta:
        get_latest_by = 'date'
        ordering = ['pos', 'date', 'type_id']

    pos = models.ForeignKey(POS, related_name='fuel_levels')
    date = models.DateTimeField(db_index=True, auto_now_add=True)
    type_id = models.IntegerField(db_index=True)
    quantity = models.IntegerField()
    consumption = models.IntegerField(default=0)

    def fuel_admin_display(self):
        fuel_name, _ = db.get_type_name(self.type_id)
        return unicode(fuel_name)
    fuel_admin_display.short_description = "Fuel"

    def __unicode__(self):
        fuel_name, _ = db.get_type_name(self.type_id)
        return u'%s: %d x %s' % (unicode(self.pos), self.quantity, fuel_name)

#------------------------------------------------------------------------------
#class FuelConsumption(models.Model):
#
#    class Meta:
#        ordering = ['pos', 'type_id']
#
#    pos = models.ForeignKey(POS, related_name='fuel_consumptions')
#    type_id = models.IntegerField() # id of fuel type
#    consumption = models.IntegerField(default=0) # consumption of this fuel type
#    stability = models.IntegerField(default=0) # stability of the estimation.
#    probable_consumption = models.IntegerField(default=0) # Most often this consumption
#    probable_stability = models.IntegerField(default=0) # nb point to reach to change stability
#
#    def fuel_admin_display(self):
#        fuelName, _ = db.get_type_name(self.typeID)
#        return unicode(fuelName)
#    fuel_admin_display.short_description = "Fuel"
#
#    def __unicode__(self):
#        fuelName, _ = db.get_type_name(self.typeID)
#        return u'%s: %s = %d / hour' % (unicode(self.pos), fuelName, self.consumption)
