'''
This file is part of ICE Security Management

Created on 18 mars 2010
@author: diabeteman
'''

from ism.core.assets.constants import STATIONS_IDS, OUTPOSTS_IDS, CONQUERABLE_STATIONS
from ism import constants
import sqlite3
from ism.data.common.models import Outpost
import threading

QUERY_ONE_TYPENAME = 'SELECT t.typeName, g.categoryID FROM invTypes t, invGroups g WHERE t.typeID=%d AND t.groupID=g.groupID;'
QUERY_TYPENAMES = 'SELECT t.typeName, g.categoryID FROM invTypes t, invGroups g WHERE t.typeID IN %s AND t.groupID=g.groupID;'
QUERY_STATION = 'SELECT stationName, stationTypeID FROM staStations WHERE stationID=%d;'
QUERY_SYSTEM = 'SELECT solarSystemName FROM mapSolarSystems WHERE solarSystemID=%d;'
QUERY_SEARCH_TYPE = 'SELECT typeID FROM invTypes WHERE published=1 AND typeName LIKE "%%%s%%";'

CACHE_TYPES = {}
LOCK_TYPES = threading.RLock()
CACHE_LOCATIONS = {}
LOCK_LOCATIONS = threading.RLock()

#------------------------------------------------------------------------------
def invalidateCache():
    with LOCATIONS_LOCK: CACHE_LOCATIONS.clear()
    # no need for invalidating the type cache.
    # the EVE database is not going to change at runtime (^^)
#------------------------------------------------------------------------------
def getCachedType(id):
    with LOCK_TYPES: return CACHE_TYPES[id]
#------------------------------------------------------------------------------
def setCachedType(id, name):
    with LOCK_TYPES: CACHE_TYPES[id] = name
#------------------------------------------------------------------------------
def getCachedLocation(id):
    with LOCK_LOCATIONS: return CACHE_LOCATIONS[id]
#------------------------------------------------------------------------------
def setCachedLocation(id, name):
    with LOCK_LOCATIONS: CACHE_LOCATIONS[id] = name
#------------------------------------------------------------------------------
def resolveTypeName(typeID):
    try:
        return getCachedType(typeID)
    except KeyError:
        #print "type cache miss", typeID
        CONN_EVE = sqlite3.connect(constants.EVE_DB_FILE)
        cursor = CONN_EVE.cursor()
        cursor.execute(QUERY_ONE_TYPENAME % typeID)
        for row in cursor :
            setCachedType(typeID, (row[0], row[1]))
            return getCachedType(typeID)
#------------------------------------------------------------------------------
def resolveTypeNames(typeIDs):
    CONN_EVE = sqlite3.connect(constants.EVE_DB_FILE)
    cursor = CONN_EVE.cursor()
    cursor.execute(QUERY_TYPENAMES % str(tuple(typeIDs)))
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
        return getCachedLocation(locationID)
    except KeyError:
        #print "location cache miss", locationID
        CONN_EVE = sqlite3.connect(constants.EVE_DB_FILE)
        cursor = CONN_EVE.cursor()
        if locationID < STATIONS_IDS :
            cursor.execute(QUERY_SYSTEM % locationID)
            for row in cursor :
                setCachedLocation(locationID, row[0])
                break
        elif locationID < OUTPOSTS_IDS :
            cursor.execute(QUERY_STATION % locationID)
            station = None
            for row in cursor :
                station = row
                break
            if station == None or station[1] in CONQUERABLE_STATIONS :
                setCachedLocation(locationID, Outpost.objects.get(stationID=locationID).stationName)
            else :
                setCachedLocation(locationID, station[0])
        else :
            setCachedLocation(locationID, Outpost.objects.get(stationID=locationID).stationName)
        
        try:
            return getCachedLocation(locationID)
        except KeyError:
            # locationID was not valid
            return ""
