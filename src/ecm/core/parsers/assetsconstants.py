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

__date__ = "2010-02-15"
__author__ = "diabeteman"



CONQUERABLE_STATIONS = (12242,12294,12295,21642,21644,21645,21646)
STATIONS_IDS = 60000000
OUTPOSTS_IDS = 61000000

NPC_LOCATION_IDS         = 66000000
CONQUERABLE_LOCATION_IDS = 67000000

NPC_LOCATION_OFFSET          = 6000001
CONQUERABLE_LOCATION_OFFSET = 6000000




BOOKMARK_TYPEID = 51
OFFICE_TYPEID = 27
HANGAR_FLAG = {62:1, 4:1000, 116:1001, 117:1002, 118:1003, 119:1004, 120:1005, 121:1006}
CARGO_FLAG  = [5].extend(range(133, 145))
SLOT_FLAG   = {'lo' : range(11, 19), 
               'med': range(19, 27), 
               'hi' : range(27, 35),
               'rig': range(92, 100),
               'sub': range(125, 133) }

# EVE inventory flags 
# They can be found in the database but this is for quicker access
FLAGS = { 0: (u'None'),
          1: (u'Wallet'),
          2: (u'Factory'),
          4: (u'Hangar'),
          5: (u'Cargo'),
          6: (u'Briefcase'),
          7: (u'Skill'),
          8: (u'Reward'),
          9: (u'Connected'),
         10: (u'Disconnected'),
         11: (u'LoSlot0'),
         12: (u'LoSlot1'),
         13: (u'LoSlot2'),
         14: (u'LoSlot3'),
         15: (u'LoSlot4'),
         16: (u'LoSlot5'),
         17: (u'LoSlot6'),
         18: (u'LoSlot7'),
         19: (u'MedSlot0'),
         20: (u'MedSlot1'),
         21: (u'MedSlot2'),
         22: (u'MedSlot3'),
         23: (u'MedSlot4'),
         24: (u'MedSlot5'),
         25: (u'MedSlot6'),
         26: (u'MedSlot7'),
         27: (u'HiSlot0'),
         28: (u'HiSlot1'),
         29: (u'HiSlot2'),
         30: (u'HiSlot3'),
         31: (u'HiSlot4'),
         32: (u'HiSlot5'),
         33: (u'HiSlot6'),
         34: (u'HiSlot7'),
         35: (u'Fixed Slot'),
         40: (u'PromenadeSlot1'),
         41: (u'PromenadeSlot2'),
         42: (u'PromenadeSlot3'),
         43: (u'PromenadeSlot4'),
         44: (u'PromenadeSlot5'),
         45: (u'PromenadeSlot6'),
         46: (u'PromenadeSlot7'),
         47: (u'PromenadeSlot8'),
         48: (u'PromenadeSlot9'),
         49: (u'PromenadeSlot10'),
         50: (u'PromenadeSlot11'),
         51: (u'PromenadeSlot12'),
         52: (u'PromenadeSlot13'),
         53: (u'PromenadeSlot14'),
         54: (u'PromenadeSlot15'),
         55: (u'PromenadeSlot16'),
         56: (u'Capsule'),
         57: (u'Pilot'),
         58: (u'Passenger'),
         59: (u'Boarding Gate'),
         60: (u'Crew'),
         61: (u'Skill In Training'),
         62: (u'CorpMarket'),
         63: (u'Locked'),
         64: (u'Unlocked'),
         70: (u'Office Slot 1'),
         71: (u'Office Slot 2'),
         72: (u'Office Slot 3'),
         73: (u'Office Slot 4'),
         74: (u'Office Slot 5'),
         75: (u'Office Slot 6'),
         76: (u'Office Slot 7'),
         77: (u'Office Slot 8'),
         78: (u'Office Slot 9'),
         79: (u'Office Slot 10'),
         80: (u'Office Slot 11'),
         81: (u'Office Slot 12'),
         82: (u'Office Slot 13'),
         83: (u'Office Slot 14'),
         84: (u'Office Slot 15'),
         85: (u'Office Slot 16'),
         86: (u'Bonus'),
         87: (u'DroneBay'),
         88: (u'Booster'),
         89: (u'Implant'),
         90: (u'ShipHangar'),
         91: (u'ShipOffline'),
         92: (u'RigSlot0'),
         93: (u'RigSlot1'),
         94: (u'RigSlot2'),
         95: (u'RigSlot3'),
         96: (u'RigSlot4'),
         97: (u'RigSlot5'),
         98: (u'RigSlot6'),
         99: (u'RigSlot7'),
        100: (u'Factory Operation'),
        116: (u'CorpSAG2'),
        117: (u'CorpSAG3'),
        118: (u'CorpSAG4'),
        119: (u'CorpSAG5'),
        120: (u'CorpSAG6'),
        121: (u'CorpSAG7'),
        122: (u'SecondaryStorage'),
        123: (u'CaptainsQuarters'),
        124: (u'Wis Promenade'),
        125: (u'SubSystem0'),
        126: (u'SubSystem1'),
        127: (u'SubSystem2'),
        128: (u'SubSystem3'),
        129: (u'SubSystem4'),
        130: (u'SubSystem5'),
        131: (u'SubSystem6'),
        132: (u'SubSystem7'),
        133: (u'SpecializedFuelBay'),
        134: (u'SpecializedOreHold'),
        135: (u'SpecializedGasHold'),
        136: (u'SpecializedMineralHold'),
        137: (u'SpecializedSalvageHold'),
        138: (u'SpecializedShipHold'),
        139: (u'SpecializedSmallShipHold'),
        140: (u'SpecializedMediumShipHold'),
        141: (u'SpecializedLargeShipHold'),
        142: (u'SpecializedIndustrialShipHold'),
        143: (u'SpecializedAmmoHold'),
        144: (u'StructureActive'),
        145: (u'StructureInactive'),
        146: (u'JunkyardReprocessed'),
        147: (u'JunkyardTrashed')}
