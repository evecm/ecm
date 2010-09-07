'''
This file is part of ICE Security Management

Created on 18 mars 2010
@author: diabeteman
'''

from ism.core.assets.constants import STATIONS_IDS, OUTPOSTS_IDS, CONQUERABLE_STATIONS
from ism import constants
import sqlite3
from ism.data.common.models import Outpost

QUERY_ONE_TYPENAME = 'SELECT t.typeName, g.categoryID FROM invTypes t, invGroups g WHERE t.typeID=%d AND t.groupID=g.groupID;'
QUERY_TYPENAMES = 'SELECT t.typeName, g.categoryID FROM invTypes t, invGroups g WHERE t.typeID IN %s AND t.groupID=g.groupID;'
QUERY_STATION = 'SELECT stationName, stationTypeID FROM staStations WHERE stationID=%d;'
QUERY_SYSTEM = 'SELECT solarSystemName FROM mapSolarSystems WHERE solarSystemID=%d;'
QUERY_SEARCH_TYPE = 'SELECT typeID FROM invTypes WHERE published=1 AND typeName LIKE "%%%s%%";'

CACHE_TYPES = {}
CACHE_LOCATIONS = {}
#------------------------------------------------------------------------------
def invalidateCache():
    CACHE_LOCATIONS.clear()
    # no need for invalidating the type cache.
    # the EVE database is not going to change at runtime (^^)
#------------------------------------------------------------------------------
def resolveTypeName(typeID):
    try:
        return CACHE_TYPES[typeID]
    except KeyError:
        CONN_EVE = sqlite3.connect(constants.EVE_DB_FILE)
        cursor = CONN_EVE.cursor()
        cursor.execute(QUERY_ONE_TYPENAME % typeID)
        for row in cursor :
            CACHE_TYPES[typeID] = (row[0], row[1])
            return CACHE_TYPES[typeID]
#------------------------------------------------------------------------------
def resolveTypeNames(typeIDs):
    CONN_EVE = sqlite3.connect(constants.EVE_DB_FILE)
    cursor = CONN_EVE.cursor()
    cursor.execute(QUERY_TYPENAMES % str(typeIDs))
    names = {}
    for row in cursor :
        names[int(row[0])] = row[1]
    return names
#------------------------------------------------------------------------------
def getMatchingIdsFromString(string):
    CONN_EVE = sqlite3.connect(constants.EVE_DB_FILE)
    cursor = CONN_EVE.cursor()
    cursor.execute(QUERY_SEARCH_TYPE % string)
    return [ id[0] for id in cursor ]
#------------------------------------------------------------------------------
def resolveLocationName(locationID):
    try:
        return CACHE_LOCATIONS[locationID]
    except KeyError:
        CONN_EVE = sqlite3.connect(constants.EVE_DB_FILE)
        cursor = CONN_EVE.cursor()
        if locationID < STATIONS_IDS :
            cursor.execute(QUERY_SYSTEM % locationID)
            for row in cursor :
                CACHE_LOCATIONS[locationID] = row[0]
                break
        elif locationID < OUTPOSTS_IDS :
            cursor.execute(QUERY_STATION % locationID)
            station = None
            for row in cursor :
                station = row
                break
            if station == None or station[1] in CONQUERABLE_STATIONS :
                CACHE_LOCATIONS[locationID] = Outpost.objects.get(stationID=locationID).stationName
            else :
                CACHE_LOCATIONS[locationID] = station[0]
        else :
            CACHE_LOCATIONS[locationID] = Outpost.objects.get(stationID=locationID).stationName
        
        return CACHE_LOCATIONS[locationID]
