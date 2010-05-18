'''
This file is part of ICE Security Management

Created on 18 mars 2010
@author: diabeteman
'''

from ism.core.assets.constants import STATIONS_IDS, OUTPOSTS_IDS, CONQUERABLE_STATIONS
from ism.constants import EVE_DB_FILE
import sqlite3
from ism.data.assets.models import Outpost



QUERY_ONE_TYPENAME = 'SELECT typeName FROM invTypes WHERE typeID=%d;'
QUERY_TYPENAMES = 'SELECT typeID, typeName FROM invTypes WHERE typeID IN %s;'
QUERY_STATION = 'SELECT stationName, stationTypeID FROM staStations WHERE stationID=%d;'
QUERY_SYSTEM = 'SELECT solarSystemName FROM mapSolarSystems WHERE solarSystemID=%d;'

def resolveTypeName(typeID):
    CONN_EVE = sqlite3.connect(EVE_DB_FILE)
    cursor = CONN_EVE.cursor()
    cursor.execute(QUERY_ONE_TYPENAME % typeID)
    for row in cursor :
        return row[0]
    
def resolveTypeNames(typeIDs):
    CONN_EVE = sqlite3.connect(EVE_DB_FILE)
    cursor = CONN_EVE.cursor()
    cursor.execute(QUERY_TYPENAMES % str(typeIDs))
    names = {}
    for row in cursor :
        names[int(row[0])] = row[1]
    return names
    
def resolveLocationName(locationID):
    CONN_EVE = sqlite3.connect(EVE_DB_FILE)
    cursor = CONN_EVE.cursor()
    if locationID < STATIONS_IDS :
        cursor.execute(QUERY_SYSTEM % locationID)
        for row in cursor :
            return row[0]
    elif locationID < OUTPOSTS_IDS :
        cursor.execute(QUERY_STATION % locationID)
        station = None
        for row in cursor :
            station = row
            break
        if station[1] in CONQUERABLE_STATIONS :
            return Outpost.objects.get(stationID=locationID).stationName
        else :
            return station[0]
    else :
        return Outpost.objects.get(stationID=locationID).stationName
