# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2011 11 2"
__author__ = "diabeteman"


STRONTIUM_CLATHRATES_TYPEID = 16275

CHARTER_MIN_SEC_STATUS = 0.45

SILO_TYPEID = 14343
SILO_VOLUME = 20000.0

CALDARI_FUEL_BLOCK_TYPEID = 4051
MINMATAR_FUEL_BLOCK_TYPEID = 4246
AMARR_FUEL_BLOCK_TYPEID = 4247
GALLENTE_FUEL_BLOCK_TYPEID = 4312

AMARR_EMPIRE_STARBASE_CHARTER = 24592
AMMATAR_MANDATE_STARBASE_CHARTER = 24597
CALDARI_STATE_STARBASE_CHARTER = 24593
GALLENTE_FEDERATION_STARBASE_CHARTER = 24594
KHANID_KINGDOM_STARBASE_CHARTER = 24596
MINMATAR_REPUBLIC_STARBASE_CHARTER = 24595

CALDARI_RACEID = 1
MINMATAR_RACEID = 2
AMARR_RACEID = 4
GALLENTE_RACEID = 8

RACE_TO_FUEL = {
    CALDARI_RACEID: CALDARI_FUEL_BLOCK_TYPEID,
    MINMATAR_RACEID: MINMATAR_FUEL_BLOCK_TYPEID,
    AMARR_RACEID: AMARR_FUEL_BLOCK_TYPEID,
    GALLENTE_RACEID: GALLENTE_FUEL_BLOCK_TYPEID,
}
FUEL_TO_RACE = {
    CALDARI_FUEL_BLOCK_TYPEID: CALDARI_RACEID,
    MINMATAR_FUEL_BLOCK_TYPEID: MINMATAR_RACEID,
    AMARR_FUEL_BLOCK_TYPEID: AMARR_RACEID,
    GALLENTE_FUEL_BLOCK_TYPEID: GALLENTE_RACEID,
}
RACEID_TO_CHARTERID = {
    500001: CALDARI_STATE_STARBASE_CHARTER,
    500002: MINMATAR_REPUBLIC_STARBASE_CHARTER,
    500003: AMARR_EMPIRE_STARBASE_CHARTER,
    500004: GALLENTE_FEDERATION_STARBASE_CHARTER,
    500007: AMMATAR_MANDATE_STARBASE_CHARTER,
    500008: KHANID_KINGDOM_STARBASE_CHARTER,
}

COMPLEX_REACTIONS = {
    16670: 10000,       #Crystalline Carbonide Reaction
    17317: 200,         #Fermionic Condensates Reaction
    16673: 10000,       #Fernite Carbide Reaction
    16683: 400,         #Ferrogel Reaction
    16679: 3000,        #Fulleride Reaction
    16682: 750,         #Hypersynaptic Fibers Reaction
    16681: 1500,        #Nanotransistors Reaction
    16680: 2200,        #Phenolic Composites Reaction
    16678: 6000,        #Sylramic Fibers Reaction
    16671: 10000,       #Titanium Carbide Reaction
    16672: 10000,       #Tungsten Carbide Reaction
}
SIMPLE_REACTIONS = {
    16663: 200,
    16659: 200,
    16660: 200,
    16655: 200,
    16668: 200,
    16656: 200,
    16669: 200,
    17769: 200,
    16665: 200,
    16666: 200,
    16667: 200,
    16662: 200,
    17960: 200,
    16657: 200,
    16658: 200,
    16664: 200,
    16661: 200,
    16654: 200,
    17959: 200,
}
UNREFINED = [
    29640,
    29641,
    29642,
    29643,
    29644,
    29645,
    29659,
    29660,
    29661,
    29662,
    29663,
    29664,
    32821,
    32822,
    32823,
    32824,
    32825,
    32826,
    32827,
    32828,
    32829,
    32830,
    32831,
    32832,
    32833,
    32834,
    32835,
    32836,
    32837,
    32838,
]
