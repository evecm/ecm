
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

__date__ = "2012 09 07"
__author__ = "tash"

from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone

#------------------------------------------------------------------------------
class Timer(models.Model):
    class Meta:
        ordering = ['timer']

    #CYCLES
    SHIELD = 0
    ARMOR = 1
    FINAL = 2
    # IHUB
    INFRASTRUCTURE_HUB = 32458 
    # POS
    AMARR_CONTROL_TOWER = 12235
    AMARR_CONTROL_TOWER_MEDIUM = 20059
    AMARR_CONTROL_TOWER_SMALL = 20060
    ANGEL_CONTROL_TOWER = 27539
    ANGEL_CONTROL_TOWER_MEDIUM = 27607
    ANGEL_CONTROL_TOWER_SMALL = 27610
    BLOOD_CONTROL_TOWER = 27530
    BLOOD_CONTROL_TOWER_MEDIUM = 27589
    BLOOD_CONTROL_TOWER_SMALL = 27592
    CALDARI_CONTROL_TOWER = 16213
    CALDARI_CONTROL_TOWER_MEDIUM = 20061
    CALDARI_CONTROL_TOWER_SMALL = 20062
    DARK_BLOOD_CONTROL_TOWER = 27532
    DARK_BLOOD_CONTROL_TOWER_MEDIUM = 27591
    DARK_BLOOD_CONTROL_TOWER_SMALL = 27594
    DOMINATION_CONTROL_TOWER = 27540
    DOMINATION_CONTROL_TOWER_MEDIUM = 27609
    DOMINATION_CONTROL_TOWER_SMALL = 27612
    DREAD_GURISTAS_CONTROL_TOWER = 27535
    DREAD_GURISTAS_CONTROL_TOWER_MEDIUM = 27597
    DREAD_GURISTAS_CONTROL_TOWER_SMALL = 27600
    GALLENTE_CONTROL_TOWER = 12236
    GALLENTE_CONTROL_TOWER_MEDIUM = 20063
    GALLENTE_CONTROL_TOWER_SMALL = 20064
    GURISTAS_CONTROL_TOWER = 27533
    GURISTAS_CONTROL_TOWER_MEDIUM = 27595
    GURISTAS_CONTROL_TOWER_SMALL = 27598
    MINMATAR_CONTROL_TOWER = 16214
    MINMATAR_CONTROL_TOWER_MEDIUM = 20065
    MINMATAR_CONTROL_TOWER_SMALL = 20066
    SANSHA_CONTROL_TOWER = 27780
    SANSHA_CONTROL_TOWER_MEDIUM = 27782
    SANSHA_CONTROL_TOWER_SMALL = 27784
    SERPENTIS_CONTROL_TOWER = 27536
    SERPENTIS_CONTROL_TOWER_MEDIUM = 27601
    SERPENTIS_CONTROL_TOWER_SMALL = 27604
    SHADOW_CONTROL_TOWER = 27538
    SHADOW_CONTROL_TOWER_MEDIUM = 27603
    SHADOW_CONTROL_TOWER_SMALL = 27606
    TRUE_SANSHA_CONTROL_TOWER = 27786
    TRUE_SANSHA_CONTROL_TOWER_MEDIUM = 27788
    TRUE_SANSHA_CONTROL_TOWER_SMALL = 27790
    # SOV UNITS
    TERRITORIAL_CLAIM_UNIT = 32226
    SOVEREIGNTY_BLOCKADE_UNIT = 32250
    # STATIONS and OUTPOSTS
    AMARR_FACTORY_OUTPOST = 21644
    AMARR_INDUSTRIAL_STATION = 1928
    AMARR_MINING_STATION = 1930
    AMARR_RESEARCH_STATION = 1931
    AMARR_STANDARD_STATION = 1929
    AMARR_STATION_HUB = 1926
    AMARR_STATION_MILITARY = 1927
    AMARR_TRADE_POST = 1932
    CALDARI_ADMINISTRATIVE_STATION = 1529
    CALDARI_FOOD_PROCESSING_PLANT_STATION = 4024
    CALDARI_LOGISTICS_STATION = 54
    CALDARI_MILITARY_STATION = 3872
    CALDARI_MINING_STATION = 4023
    CALDARI_RESEARCH_OUTPOST = 21642
    CALDARI_RESEARCH_STATION = 1530
    CALDARI_STATION_HUB = 3871
    CALDARI_TRADING_STATION = 1531
    GALLENTE_ADMINISTRATIVE_OUTPOST = 21645
    GALLENTE_ADMINISTRATIVE_STATION = 3868
    GALLENTE_INDUSTRIAL_STATION = 3867
    GALLENTE_LOGISTICS_STATION = 3869
    GALLENTE_MILITARY_STATION = 56
    GALLENTE_MINING_STATION = 3870
    GALLENTE_RESEARCH_STATION = 3865
    GALLENTE_STATION_HUB = 57
    GALLENTE_TRADING_HUB = 3866
    MINMATAR_HUB = 2496
    MINMATAR_INDUSTRIAL_STATION = 2497
    MINMATAR_MILITARY_STATION = 2498
    MINMATAR_MINING_STATION = 2499
    MINMATAR_RESEARCH_STATION = 2500
    MINMATAR_SERVICE_OUTPOST = 21646
    MINMATAR_STATION = 2501
    MINMATAR_TRADE_POST = 2502

    STRUCTURE_CHOICE = (
        ('IHUB', (
            (INFRASTRUCTURE_HUB, "Infrastructure Hub"),
            )
        ),
        ('Control Tower', (
            (AMARR_CONTROL_TOWER, "Amarr Control Tower"),
            (AMARR_CONTROL_TOWER_MEDIUM, "Amarr Control Tower Medium"),
            (AMARR_CONTROL_TOWER_SMALL, "Amarr Control Tower Small"),
            (ANGEL_CONTROL_TOWER, "Angel Control Tower"),
            (ANGEL_CONTROL_TOWER_MEDIUM, "Angel Control Tower Medium"),
            (ANGEL_CONTROL_TOWER_SMALL, "Angel Control Tower Small"),
            (BLOOD_CONTROL_TOWER, "Blood Control Tower"),
            (BLOOD_CONTROL_TOWER_MEDIUM, "Blood Control Tower Medium"),
            (BLOOD_CONTROL_TOWER_SMALL, "Blood Control Tower Small"),
            (CALDARI_CONTROL_TOWER, "Caldari Control Tower"),
            (CALDARI_CONTROL_TOWER_MEDIUM, "Caldari Control Tower Medium"),
            (CALDARI_CONTROL_TOWER_SMALL, "Caldari Control Tower Small"),
            (DARK_BLOOD_CONTROL_TOWER, "Dark Blood Control Tower"),
            (DARK_BLOOD_CONTROL_TOWER_MEDIUM, "Dark Blood Control Tower Medium"),
            (DARK_BLOOD_CONTROL_TOWER_SMALL, "Dark Blood Control Tower Small"),
            (DOMINATION_CONTROL_TOWER, "Domination Control Tower"),
            (DOMINATION_CONTROL_TOWER_MEDIUM, "Domination Control Tower Medium"),
            (DOMINATION_CONTROL_TOWER_SMALL, "Domination Control Tower Small"),
            (DREAD_GURISTAS_CONTROL_TOWER, "Dread Guristas Control Tower"),
            (DREAD_GURISTAS_CONTROL_TOWER_MEDIUM, "Dread Guristas Control Tower Medium"),
            (DREAD_GURISTAS_CONTROL_TOWER_SMALL, "Dread Guristas Control Tower Small"),
            (GALLENTE_CONTROL_TOWER, "Gallente Control Tower"),
            (GALLENTE_CONTROL_TOWER_MEDIUM, "Gallente Control Tower Medium"),
            (GALLENTE_CONTROL_TOWER_SMALL, "Gallente Control Tower Small"),
            (GURISTAS_CONTROL_TOWER, "Guristas Control Tower"),
            (GURISTAS_CONTROL_TOWER_MEDIUM, "Guristas Control Tower Medium"),
            (GURISTAS_CONTROL_TOWER_SMALL, "Guristas Control Tower Small"),
            (MINMATAR_CONTROL_TOWER, "Minmatar Control Tower"),
            (MINMATAR_CONTROL_TOWER_MEDIUM, "Minmatar Control Tower Medium"),
            (MINMATAR_CONTROL_TOWER_SMALL, "Minmatar Control Tower Small"),
            (SANSHA_CONTROL_TOWER, "Sansha Control Tower"),
            (SANSHA_CONTROL_TOWER_MEDIUM, "Sansha Control Tower Medium"),
            (SANSHA_CONTROL_TOWER_SMALL, "Sansha Control Tower Small"),
            (SERPENTIS_CONTROL_TOWER, "Serpentis Control Tower"),
            (SERPENTIS_CONTROL_TOWER_MEDIUM, "Serpentis Control Tower Medium"),
            (SERPENTIS_CONTROL_TOWER_SMALL, "Serpentis Control Tower Small"),
            (SHADOW_CONTROL_TOWER, "Shadow Control Tower"),
            (SHADOW_CONTROL_TOWER_MEDIUM, "Shadow Control Tower Medium"),
            (SHADOW_CONTROL_TOWER_SMALL, "Shadow Control Tower Small"),
            (TRUE_SANSHA_CONTROL_TOWER, "True Sansha Control Tower"),
            (TRUE_SANSHA_CONTROL_TOWER_MEDIUM, "True Sansha Control Tower Medium"),
            (TRUE_SANSHA_CONTROL_TOWER_SMALL, "True Sansha Control Tower Small"),
            )
        ),
        ('SOV Modules', (
            (TERRITORIAL_CLAIM_UNIT, "Territorial Claim Unit"),
            (SOVEREIGNTY_BLOCKADE_UNIT, "Sovereignty Blockade Unit"),
            ),
        ),
        ('Outposts', (
            (AMARR_FACTORY_OUTPOST, "Amarr Factory Outpost"),
            (CALDARI_RESEARCH_OUTPOST, "Caldari Research Outpost"),
            (GALLENTE_ADMINISTRATIVE_OUTPOST, "Gallente Administrative Outpost"),
            (MINMATAR_SERVICE_OUTPOST, "Minmatar Service Outpost"),
            ),
        ),
        ('Stations', (
            (AMARR_INDUSTRIAL_STATION, "Amarr Industrial Station"),
            (AMARR_MINING_STATION, "Amarr Mining Station"),
            (AMARR_RESEARCH_STATION, "Amarr Research Station"),
            (AMARR_STANDARD_STATION, "Amarr Standard Station"),
            (AMARR_STATION_HUB, "Amarr Station Hub"),
            (AMARR_STATION_MILITARY, "Amarr Station Military"),
            (AMARR_TRADE_POST, "Amarr Trade Post"),
            (CALDARI_ADMINISTRATIVE_STATION, "Caldari Administrative Station"),
            (CALDARI_FOOD_PROCESSING_PLANT_STATION, "Caldari Food Processing Plant Station"),
            (CALDARI_LOGISTICS_STATION, "Caldari Logistics Station"),
            (CALDARI_MILITARY_STATION, "Caldari Military Station"),
            (CALDARI_MINING_STATION, "Caldari Mining Station"),
            (CALDARI_RESEARCH_STATION, "Caldari Research Station"),
            (CALDARI_STATION_HUB, "Caldari Station Hub"),
            (CALDARI_TRADING_STATION, "Caldari Trading Station"),
            (GALLENTE_ADMINISTRATIVE_STATION, "Gallente Administrative Station"),
            (GALLENTE_INDUSTRIAL_STATION, "Gallente Industrial Station"),
            (GALLENTE_LOGISTICS_STATION, "Gallente Logistics Station"),
            (GALLENTE_MILITARY_STATION, "Gallente Military Station"),
            (GALLENTE_MINING_STATION, "Gallente Mining Station"),
            (GALLENTE_RESEARCH_STATION, "Gallente Research Station"),
            (GALLENTE_STATION_HUB, "Gallente Station Hub "),
            (GALLENTE_TRADING_HUB, "Gallente Trading Hub"),
            (MINMATAR_HUB, "Minmatar Hub"),
            (MINMATAR_INDUSTRIAL_STATION, "Minmatar Industrial Station"),
            (MINMATAR_MILITARY_STATION, "Minmatar Military Station"),
            (MINMATAR_MINING_STATION, "Minmatar Mining Station"),
            (MINMATAR_RESEARCH_STATION, "Minmatar Research Station"),
            (MINMATAR_STATION, "Minmatar Station"),
            (MINMATAR_TRADE_POST, "Minmatar Trade Post")
            ),
        )
    )

    CYCLE_CHOICES = (
        (SHIELD, "Shield"),
        (ARMOR, "Armor"),
        (FINAL, "Final"),
    )

    structure = models.BigIntegerField(choices=STRUCTURE_CHOICE, default=AMARR_FACTORY_OUTPOST)
    timer = models.DateTimeField(db_index=True)
    location_id = models.BigIntegerField(default=0)
    location = models.CharField(max_length=255, default="")
    notes = models.TextField(null=True, blank=True)
    cycle = models.IntegerField(choices=CYCLE_CHOICES, default=SHIELD)
    friendly = models.BooleanField(default=False)
    owner_id = models.BigIntegerField(default=0)
    owner = models.TextField(null=True, blank=True)


    def exit_time(self):
        base_time = self.timer + 48
        return (base_time - 3, base_time + 3)

    def cycle_label(self):
        for choice in self.CYCLE_CHOICES:
            if self.cycle in choice:
                return choice[1] 

    def structure_label(self):
        for choice in self.STRUCTURE_CHOICE:
            for category in choice:
                for entry in category:
                    if self.structure == entry[0]:
                        return entry[1]

    def location_label(self):
        if self.location:
            return self.location.split()[0]
        else:
            return ''
    
    def location_dotlan(self):
        if self.location:
            # ingame: Jita III - Moon 1
            # DOTLAN: Jita/III-Moon-1
            return self.location.split()[0] + '/' + '-'.join(self.location.replace(' - ', '-').split()[1:])
        else:
            return ''

    def __eq__(self, other):
        return self.timer == other.timer

    def __cmp__(self, other):
        return cmp(self.timer, other.timer)
