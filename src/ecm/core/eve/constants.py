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




DECRYPTORS = {
#            typeID   CHANCE_mod   ME_mod   PE_mod   RUNS_mod  typeName
# Amarr Interface                                              
    728: (                                                     
            (23178,   1.1,         3,       3,       0,        "Formation Layout"),
            (23179,   1.2,         2,       5,       1,        "Classic Doctrine"),
            (23180,   1.0,         1,       4,       2,        "Sacred Manifesto"),
            (23182,   1.8,        -1,       2,       4,        "War Strategon"),
            (23181,   0.6,        -2,       1,       9,        "Circular Logic")
         ),                                                    
# Minmatar Interface                                           
    729: (                                                     
            (21579,   1.1,         3,       3,       0,        "Calibration Data"),
            (21580,   1.2,         2,       5,       1,        "Advanced Theories"),
            (21581,   1.0,         1,       4,       2,        "Operation Handbook"),
            (21583,   1.8,        -1,       2,       4,        "Assembly Instructions"),
            (21582,   0.6,        -2,       1,       9,        "Circuitry Schematics")
         ),                                                    
# Gallente Interface                                           
    730: (                                                     
            (23183,   1.1,         3,       3,       0,        "Collision Measurements"),
            (23184,   1.2,         2,       5,       1,        "Test Reports"),
            (23185,   1.0,         1,       4,       2,        "Engagement Plan"),
            (23187,   1.8,        -1,       2,       4,        "Stolen Formulas"),
            (23186,   0.6,        -2,       1,       9,        "Symbiotic Figures")
         ),                                                    
# Caldalol Interface                                           
    731: (                                                     
            (21573,   1.1,         3,       3,       0,        "Tuning Instructions"),
            (21574,   1.2,         2,       5,       1,        "Prototype Diagram"),
            (21575,   1.0,         1,       4,       2,        "User Manual"),
            (21577,   1.8,        -1,       2,       4,        "Installation Guide"),
            (21576,   0.6,        -2,       1,       9,        "Interface Alignment Chart")
         )
}
DATA_INTERFACES_GROUP_ID = 716

INTERFACES_DECRYPTOR_MAPPING = {
#   typeID   decryptorGroup   interfaceName
# Amarr
    25554:   728,             # Occult Data Interface
    25851:   728,             # Occult Ship Data Interface
    26603:   728,             # Occult Tuner Data Interface
# Minmatar                
    25553:   729,             # Cryptic Data Interface
    25857:   729,             # Cryptic Ship Data Interface
    26597:   729,             # Cryptic Tuner Data Interface
# Gallente                
    25556:   730,             # Incognito Data Interface
    25855:   730,             # Incognito Ship Data Interface
    26601:   730,             # Incognito Tuner Data Interface
# Caldalol                
    25555:   731,             # Esoteric Data Interface
    25853:   731,             # Esoteric Ship Data Interface
    26599:   731,             # Esoteric Tuner Data Interface
}
