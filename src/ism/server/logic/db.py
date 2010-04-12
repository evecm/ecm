'''
This file is part of ICE Security Management

Created on 18 mars 2010
@author: diabeteman
'''

import sqlite3
from ISM.constants import EVE_DB_FILE
from ISM.constants import CONQUERABLE_STATIONS, STATIONS_IDS, OUTPOSTS_IDS

CONN_EVE = sqlite3.connect(EVE_DB_FILE)

QUERY_ONE_TYPENAME = 'SELECT typeName FROM invTypes WHERE typeID=%d;'
QUERY_TYPENAMES = 'SELECT typeID, typeName FROM invTypes WHERE typeID IN %s;'
QUERY_STATION = 'SELECT stationName, stationTypeID FROM staStations WHERE stationID=%d;'
QUERY_OUTPOST = 'SELECT outpostName FROM staOutposts WHERE outpostID=%d;'

def resolveTypeName(typeID):
    cursor = CONN_EVE.cursor()
    cursor.execute(QUERY_ONE_TYPENAME % typeID)
    for row in cursor :
        return row[0]
    
def resolveTypeNames(typeIDs):
    cursor = CONN_EVE.cursor()
    cursor.execute(QUERY_TYPENAMES % str(typeIDs))
    names = {}
    for row in cursor :
        names[int(row[0])] = row[1]
    return names
    
def resolveStationName(stationID):
    cursor = CONN_EVE.cursor()
    if stationID < STATIONS_IDS :
        pass
    elif stationID < OUTPOSTS_IDS :
        cursor.execute(QUERY_STATION % stationID)
        station = None
        for row in cursor :
            station = row
            break
        if station[1] in CONQUERABLE_STATIONS :
            cursor.execute(QUERY_OUTPOST % stationID)
            for row in cursor :
                return row[0]
        else :
            return station[0]
    else :
        cursor.execute(QUERY_OUTPOST % stationID)
        for row in cursor :
            return row[0]
