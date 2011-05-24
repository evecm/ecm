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

__date__ = "2010-03-18"
__author__ = "diabeteman"


import threading

from django.db import connections

import ecm.core.parsers.assetsconstants as cst
from ecm.data.common.models import Outpost

EVE_DB = connections['eve']

#------------------------------------------------------------------------------
CACHE_OUTPOSTS = {}
LOCK_OUTPOSTS = threading.RLock()
def invalidateCache():
    with LOCK_OUTPOSTS: CACHE_OUTPOSTS.clear()
    # no need for invalidating the other caches
    # the EVE database is not going to change at runtime (^^)
#------------------------------------------------------------------------------
CACHE_TYPES = {}
LOCK_TYPES = threading.RLock()
def getCachedType(id):
    with LOCK_TYPES: return CACHE_TYPES[id]
#------------------------------------------------------------------------------
def setCachedType(id, name):
    with LOCK_TYPES: CACHE_TYPES[id] = name
#------------------------------------------------------------------------------
CACHE_LOCATIONS = {}
LOCK_LOCATIONS = threading.RLock()
def getCachedLocation(id):
    try:
        with LOCK_LOCATIONS: return CACHE_LOCATIONS[id]
    except KeyError:
        with LOCK_OUTPOSTS: return CACHE_OUTPOSTS[id]
#------------------------------------------------------------------------------
def setCachedLocation(id, name, security=0):
    with LOCK_LOCATIONS: CACHE_LOCATIONS[id] = (name, security)
#------------------------------------------------------------------------------
def setCachedOutpost(id, name):
    with LOCK_OUTPOSTS: CACHE_OUTPOSTS[id] = (name, 0)
#------------------------------------------------------------------------------
QUERY_ONE_TYPENAME = 'SELECT t.typeName, g.categoryID '\
                     'FROM "invTypes" t, "invGroups" g '\
                     'WHERE t.typeID=%s AND t.groupID=g.groupID;'
def resolveTypeName(typeID):
    try:
        return getCachedType(typeID)
    except KeyError:
        #print "type cache miss", typeID
        #EVE_DB = sqlite3.connect(settings.EVE_DB_FILE)
        cursor = EVE_DB.cursor()
        cursor.execute(QUERY_ONE_TYPENAME, [typeID])
        for typeName, categoryID in cursor:
            setCachedType(typeID, (typeName, categoryID))
        cursor.close() 
        return getCachedType(typeID)
#------------------------------------------------------------------------------
QUERY_TYPENAMES = 'SELECT t.typeName, g.categoryID '\
                  'FROM invTypes t, invGroups g '\
                  'WHERE t.typeID IN %s AND t.groupID=g.groupID;'
def resolveTypeNames(typeIDs):
    #EVE_DB = sqlite3.connect(settings.EVE_DB_FILE)
    cursor = EVE_DB.cursor()
    ids_str = str(typeIDs).replace("[", "(").replace("]", ")")
    cursor.execute(QUERY_TYPENAMES % ids_str)
    names = {}
    for row in cursor:
        names[int(row[0])] = row[1]
    cursor.close()
    return names
#------------------------------------------------------------------------------
QUERY_SEARCH_TYPE = 'SELECT "typeID" FROM "invTypes" '\
                    'WHERE "published"=1 AND "typeName" LIKE %s;'
def getMatchingIdsFromString(string):
    #EVE_DB = sqlite3.connect(settings.EVE_DB_FILE)
    cursor = EVE_DB.cursor()
    cursor.execute(QUERY_SEARCH_TYPE, [ "%" + string + "%" ])
    ids = []
    for id, in cursor:
        ids.append(id)
    cursor.close()
    return ids

#------------------------------------------------------------------------------
LOCK_SOLARSYSTEMS = threading.RLock()
CACHE_SOLARSYSTEMS = {}
QUERY_SOLARSYST = 'SELECT "solarSystemID" FROM "staStations" WHERE "stationID"=%s;'
def getSolarSystemID(stationID):
    try:
        with LOCK_SOLARSYSTEMS:
            return CACHE_SOLARSYSTEMS[stationID]
    except KeyError:
        try:
            #EVE_DB = sqlite3.connect(settings.EVE_DB_FILE)
            cursor = EVE_DB.cursor()
            cursor.execute(QUERY_SOLARSYST, [stationID])
            for solarSystemID, in cursor:
                with LOCK_SOLARSYSTEMS:
                    CACHE_SOLARSYSTEMS[stationID] = solarSystemID
            cursor.close()
            with LOCK_SOLARSYSTEMS:
                return CACHE_SOLARSYSTEMS[stationID]
        except KeyError:
            try:
                with LOCK_SOLARSYSTEMS:
                    CACHE_SOLARSYSTEMS[stationID] = Outpost.objects.get(stationID=stationID).solarSystemID
            except Outpost.DoesNotExist:
                # outpost has not been parsed yet
                with LOCK_SOLARSYSTEMS: CACHE_SOLARSYSTEMS[stationID] = 0
            with LOCK_SOLARSYSTEMS:
                return CACHE_SOLARSYSTEMS[stationID]
#------------------------------------------------------------------------------
QUERY_STATION = 'SELECT "stationName", "stationTypeID" '\
                'FROM "staStations" WHERE "stationID"=%s;'
QUERY_SYSTEM = 'SELECT "solarSystemName", "security" '\
               'FROM "mapSolarSystems" WHERE "solarSystemID"=%s;'
def resolveLocationName(locationID):
    try:
        return getCachedLocation(locationID)
    except KeyError:
        #print "location cache miss", locationID
        #EVE_DB = sqlite3.connect(settings.EVE_DB_FILE)
        cursor = EVE_DB.cursor()
        if locationID < cst.STATIONS_IDS:
            cursor.execute(QUERY_SYSTEM, [locationID])
            for name, security in cursor:
                setCachedLocation(id=locationID, name=name, security=security)
        elif locationID < cst.OUTPOSTS_IDS:
            cursor.execute(QUERY_STATION, [locationID])
            stationName, stationTypeID = None, None
            for stationName, stationTypeID in cursor: pass
            if stationTypeID in cst.CONQUERABLE_STATIONS:
                setCachedOutpost(locationID, Outpost.objects.get(stationID=locationID).stationName)
            else:
                setCachedLocation(id=locationID, name=stationName)
        else:
            setCachedOutpost(locationID, Outpost.objects.get(stationID=locationID).stationName)
        cursor.close()
        try:
            return getCachedLocation(locationID)
        except KeyError:
            # locationID was not valid
            return ("", 0.0)

