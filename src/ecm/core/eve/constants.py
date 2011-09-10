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

__date__ = "2010-02-15"
__author__ = "diabeteman"



CONQUERABLE_STATIONS = (12242, 12294, 12295, 21642, 21644, 21645, 21646)

STATIONS_IDS = 60000000
OUTPOSTS_IDS = 61000000

MAX_STATION_ID = 62000000

BOOKMARK_TYPEID = 51
OFFICE_TYPEID = 27
HAS_HANGAR_DIVISIONS = {
#  typeID: has_hangar_divisions 
    
    # MISC
    17621: True, # Corporate Hangar Array
    12237: False, # Ship Maintenance Array
    24646: False, # Capital Ship Maintenance Array
    27897: False, # Jump Bridge
    25821: False, # General Storage

    # ASSEMBLY ARRAYS
    13780: True, # Equipment Assembly Array
    16220: True, # Rapid Equipment Assembly Array
    24574: True, # Small Ship Assembly Array
    24575: True, # Capital Ship Assembly Array
    24653: True, # Advanced Small Ship Assembly Array
    24654: True, # Medium Ship Assembly Array
    24655: True, # Advanced Medium Ship Assembly Array
    24656: True, # X-Large Ship Assembly Array
    24657: True, # Advanced Large Ship Assembly Array
    24658: True, # Ammunition Assembly Array
    24659: True, # Drone Assembly Array
    24660: True, # Component Assembly Array
    29613: True, # Large Ship Assembly Array
    30389: True, # Subsystem Assembly Array

    # LABORATORIES
    16216: True, # Mobile Laboratory
    28351: True, # Advanced Mobile Laboratory
    24567: True, # Experimental Laboratory
    32245: True, # Hyasyoda Mobile Laboratory

    # MINING & REACTIONS
    14343: False, # Silo
    25270: False, # Biochemical Silo
    25271: False, # Catalyst Silo
    30655: False, # Hybrid Polymer Silo
    25305: False, # Drug Lab
    25280: False, # Hazardous Chemical Silo
    12238: False, # Refining Array
    12239: False, # Medium Intensive Refining Array
    19470: False, # Intensive Refining Array

    # CONTAINERS
     3465: False, # Large Secure Container
     3466: False, # Medium Secure Container
     3467: False, # Small Secure Container
    11488: False, # Huge Secure Container
    11489: False, # Giant Secure Container
}

HANGAR_FLAG = {62:1, 4:1000, 116:1001, 117:1002, 118:1003, 119:1004, 120:1005, 121:1006}
CARGO_FLAG = [5].extend(range(133, 145))
SLOT_FLAG = {'lo' : range(11, 19),
               'med': range(19, 27),
               'hi' : range(27, 35),
               'rig': range(92, 100),
               'sub': range(125, 133) }




# EVE inventory flags 
# They can be found in the database but this is for quicker access
FLAGS = { 
      0: 'None',
      1: 'Wallet',
      2: 'Factory',
      4: 'Hangar',
      5: 'Cargo',
      6: 'Briefcase',
      7: 'Skill',
      8: 'Reward',
      9: 'Connected',
     10: 'Disconnected',
     11: 'LoSlot0',
     12: 'LoSlot1',
     13: 'LoSlot2',
     14: 'LoSlot3',
     15: 'LoSlot4',
     16: 'LoSlot5',
     17: 'LoSlot6',
     18: 'LoSlot7',
     19: 'MedSlot0',
     20: 'MedSlot1',
     21: 'MedSlot2',
     22: 'MedSlot3',
     23: 'MedSlot4',
     24: 'MedSlot5',
     25: 'MedSlot6',
     26: 'MedSlot7',
     27: 'HiSlot0',
     28: 'HiSlot1',
     29: 'HiSlot2',
     30: 'HiSlot3',
     31: 'HiSlot4',
     32: 'HiSlot5',
     33: 'HiSlot6',
     34: 'HiSlot7',
     35: 'Fixed Slot',
     40: 'PromenadeSlot1',
     41: 'PromenadeSlot2',
     42: 'PromenadeSlot3',
     43: 'PromenadeSlot4',
     44: 'PromenadeSlot5',
     45: 'PromenadeSlot6',
     46: 'PromenadeSlot7',
     47: 'PromenadeSlot8',
     48: 'PromenadeSlot9',
     49: 'PromenadeSlot10',
     50: 'PromenadeSlot11',
     51: 'PromenadeSlot12',
     52: 'PromenadeSlot13',
     53: 'PromenadeSlot14',
     54: 'PromenadeSlot15',
     55: 'PromenadeSlot16',
     56: 'Capsule',
     57: 'Pilot',
     58: 'Passenger',
     59: 'Boarding Gate',
     60: 'Crew',
     61: 'Skill In Training',
     62: 'CorpMarket',
     63: 'Locked',
     64: 'Unlocked',
     70: 'Office Slot 1',
     71: 'Office Slot 2',
     72: 'Office Slot 3',
     73: 'Office Slot 4',
     74: 'Office Slot 5',
     75: 'Office Slot 6',
     76: 'Office Slot 7',
     77: 'Office Slot 8',
     78: 'Office Slot 9',
     79: 'Office Slot 10',
     80: 'Office Slot 11',
     81: 'Office Slot 12',
     82: 'Office Slot 13',
     83: 'Office Slot 14',
     84: 'Office Slot 15',
     85: 'Office Slot 16',
     86: 'Bonus',
     87: 'DroneBay',
     88: 'Booster',
     89: 'Implant',
     90: 'ShipHangar',
     91: 'ShipOffline',
     92: 'RigSlot0',
     93: 'RigSlot1',
     94: 'RigSlot2',
     95: 'RigSlot3',
     96: 'RigSlot4',
     97: 'RigSlot5',
     98: 'RigSlot6',
     99: 'RigSlot7',
    100: 'Factory Operation',
    116: 'CorpSAG2',
    117: 'CorpSAG3',
    118: 'CorpSAG4',
    119: 'CorpSAG5',
    120: 'CorpSAG6',
    121: 'CorpSAG7',
    122: 'SecondaryStorage',
    123: 'CaptainsQuarters',
    124: 'Wis Promenade',
    125: 'SubSystem0',
    126: 'SubSystem1',
    127: 'SubSystem2',
    128: 'SubSystem3',
    129: 'SubSystem4',
    130: 'SubSystem5',
    131: 'SubSystem6',
    132: 'SubSystem7',
    133: 'SpecializedFuelBay',
    134: 'SpecializedOreHold',
    135: 'SpecializedGasHold',
    136: 'SpecializedMineralHold',
    137: 'SpecializedSalvageHold',
    138: 'SpecializedShipHold',
    139: 'SpecializedSmallShipHold',
    140: 'SpecializedMediumShipHold',
    141: 'SpecializedLargeShipHold',
    142: 'SpecializedIndustrialShipHold',
    143: 'SpecializedAmmoHold',
    144: 'StructureActive',
    145: 'StructureInactive',
    146: 'JunkyardReprocessed',
    147: 'JunkyardTrashed'
}
