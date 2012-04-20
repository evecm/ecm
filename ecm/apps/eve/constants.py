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

CONTROL_TOWERS = {
    12235: False, # Amarr Control Tower
    12236: False, # Gallente Control Tower
    16213: False, # Caldari Control Tower
    16214: False, # Minmatar Control Tower
    20059: False, # Amarr Control Tower Medium
    20060: False, # Amarr Control Tower Small
    20061: False, # Caldari Control Tower Medium
    20062: False, # Caldari Control Tower Small
    20063: False, # Gallente Control Tower Medium
    20064: False, # Gallente Control Tower Small
    20065: False, # Minmatar Control Tower Medium
    20066: False, # Minmatar Control Tower Small
    27530: False, # Blood Control Tower
    27532: False, # Dark Blood Control Tower
    27533: False, # Guristas Control Tower
    27535: False, # Dread Guristas Control Tower
    27536: False, # Serpentis Control Tower
    27538: False, # Shadow Control Tower
    27539: False, # Angel Control Tower
    27540: False, # Domination Control Tower
    27589: False, # Blood Control Tower Medium
    27591: False, # Dark Blood Control Tower Medium
    27592: False, # Blood Control Tower Small
    27594: False, # Dark Blood Control Tower Small
    27595: False, # Guristas Control Tower Medium
    27597: False, # Dread Guristas Control Tower Medium
    27598: False, # Guristas Control Tower Small
    27600: False, # Dread Guristas Control Tower Small
    27601: False, # Serpentis Control Tower Medium
    27603: False, # Shadow Control Tower Medium
    27604: False, # Serpentis Control Tower Small
    27606: False, # Shadow Control Tower Small
    27607: False, # Angel Control Tower Medium
    27609: False, # Domination Control Tower Medium
    27610: False, # Angel Control Tower Small
    27612: False, # Domination Control Tower Small
    27780: False, # Sansha Control Tower
    27782: False, # Sansha Control Tower Medium
    27784: False, # Sansha Control Tower Small
    27786: False, # True Sansha Control Tower
    27788: False, # True Sansha Control Tower Medium
    27790: False, # True Sansha Control Tower Small
}
HAS_HANGAR_DIVISIONS.update(CONTROL_TOWERS)

HANGAR_FLAG = {62:1, 4:1000, 116:1001, 117:1002, 118:1003, 119:1004, 120:1005, 121:1006}
CARGO_FLAG = [5].extend(range(133, 145))
SLOT_FLAG = {'lo' : range(11, 19),
             'med': range(19, 27),
             'hi' : range(27, 35),
             'rig': range(92, 100),
             'sub': range(125, 133) }


STATIONS_GROUPID = 15
CELESTIAL_CATEGORYID = 2
BLUEPRINTS_CATEGORYID = 9
FACTION_FRIGATES_TYPEIDS = (2836, 17922, 29266, 17928, 17932, 3532, 32207, 32209)
TECH1_METAGRP_ID = 0
TECH2_METAGRP_ID = 2
TECH3_METAGRP_ID = 14
MANUFACTURABLE_ITEMS = (TECH1_METAGRP_ID, TECH2_METAGRP_ID, TECH3_METAGRP_ID)
SHIP_CATEGORYID = 6
MODULE_CATEGORYID = 7
CHARGE_CATEGORYID = 8

CAPITAL_SHIPS_GROUPID = (
    485, # dread
    547, # carrier
    659, # supercarrier
    883, # capital industrial
    513, # freighter
    941, # industrial command ship
    902, # jump freighter
    30,  # titan
)
