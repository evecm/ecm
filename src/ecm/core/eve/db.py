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

__date__ = "2010-03-18"
__author__ = "diabeteman"

from django.db import connections
from ecm.core.eve import cache


EVE_DB = connections['eve']

#------------------------------------------------------------------------------
QUERY_ONE_TYPENAME = 'SELECT "typeName", "categoryID" FROM "invTypes" WHERE "typeID" = %s;'
def get_type_name(typeID):
    try:
        return cache.getCachedTypeName(typeID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(QUERY_ONE_TYPENAME, [typeID])
        for typeName, categoryID in cursor:
            cache.setCachedTypeName(typeID, (typeName, categoryID))
        cursor.close()
        try:
            return cache.getCachedTypeName(typeID)
        except KeyError:
            return ("???", 0)

#------------------------------------------------------------------------------
QUERY_TYPENAMES = 'SELECT "typeID", "typeName", "categoryID" FROM "invTypes" WHERE "typeID" IN %s;'
def get_type_names(typeIDs):
    cursor = EVE_DB.cursor()
    cursor.execute(QUERY_TYPENAMES, [typeIDs])
    names = {}
    for typeID, typeName, categoryID in cursor:
        names[typeID] = (typeName, categoryID)
        cache.setCachedTypeName(typeID, (typeName, categoryID))
    cursor.close()
    return names

#------------------------------------------------------------------------------
SQL_CELESTIAL_OBJECTS = '''SELECT "itemID", "x", "y", "z" 
FROM "mapCelestialObjects" 
WHERE "solarSystemID" = %s
  AND "groupID" IN (7, 8);''' # only planets & moons
def get_celestial_objects(solarSystemID):
    try:
        return cache.get_cached_celestial_objects(solarSystemID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(SQL_CELESTIAL_OBJECTS, [solarSystemID])
        objects = cursor.fetchall()
        cursor.close()
        cache.set_cached_celestial_objects(solarSystemID, objects)
        return objects

#------------------------------------------------------------------------------
SQL_CELESTIAL_OBJ = '''SELECT "solarSystemID", "x", "y", "z" 
FROM "mapCelestialObjects" 
WHERE "itemID" = %s;'''
def get_celestial_object(itemID):
    cursor = EVE_DB.cursor()
    cursor.execute(SQL_CELESTIAL_OBJ, [itemID])
    solarSystemID, x, y, z = cursor.fetchone()
    cursor.close()
    return solarSystemID, x, y, z

#------------------------------------------------------------------------------
QUERY_SEARCH_TYPE = 'SELECT "typeID" FROM "invTypes" WHERE "typeName" LIKE %s;'
def getMatchingIdsFromString(string):
    cursor = EVE_DB.cursor()
    cursor.execute(QUERY_SEARCH_TYPE, [ "%" + string + "%" ])
    ids = []
    for typeID, in cursor:
        ids.append(typeID)
    cursor.close()
    return ids

#------------------------------------------------------------------------------
QUERY_SOLARSYST = 'SELECT "solarSystemID" FROM "mapCelestialObjects" WHERE "itemID"=%s;'
def getSolarSystemID(stationID):
    try:
        return cache.getCachedSolarSystemID(stationID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(QUERY_SOLARSYST, [stationID])
        for solarSystemID, in cursor:
            cache.setCachedSolarSystemID(stationID, solarSystemID)
        cursor.close()
        try:
            return cache.getCachedSolarSystemID(stationID)
        except KeyError:
            return 0

#------------------------------------------------------------------------------
QUERY_LOCATION = 'SELECT "itemName", "security" FROM "mapCelestialObjects" WHERE "itemID"=%s;'
def resolveLocationName(locationID):
    try:
        return cache.getCachedLocation(locationID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(QUERY_LOCATION, [locationID])
        for itemName, security in cursor:
            cache.setCachedLocation(locID=locationID, name=itemName, security=security)
        cursor.close()
        try:
            return cache.getCachedLocation(locationID)
        except KeyError:
            # locationID was not valid
            return ("???", 0.0)

#------------------------------------------------------------------------------
SQL_UPDATE_OUTPOST_NAME = 'UPDATE mapCelestialObjects SET itemName=%s WHERE itemID=%s;'
SQL_NEW_OUTPOST = '''INSERT INTO mapCelestialObjects
(itemID, typeID, groupID, solarSystemID, regionID, itemName, security)
VALUES (%s, 0, 0, %s, 0, %s, %s);'''
def updateLocationName(stationID, solarSystemID, locationName):
    oldName, security = resolveLocationName(stationID)
    cursor = EVE_DB.cursor()
    if oldName == '???':
        cursor.execute('SELECT security FROM mapCelestialObjects WHERE itemID = %s;', [solarSystemID])
        security, = cursor.fetchone()
        if security is None:
            security = 0.0
        cursor.execute(SQL_NEW_OUTPOST, [stationID, solarSystemID, locationName, security])
        created = True
    else:
        cursor.execute(SQL_UPDATE_OUTPOST_NAME, [locationName, stationID])
        created = False
    cache.setCachedLocation(stationID, locationName, security)
    cursor.close()
    return created

#------------------------------------------------------------------------------
SQL_MKTGRP = '''SELECT marketGroupID, marketGroupName, hasTypes
FROM invMarketGroups
WHERE marketGroupID = %s;'''
def getMarketGroup(marketGroupID):
    try:
        return cache.getCachedMarketGroup(marketGroupID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(SQL_MKTGRP, [marketGroupID])
        row = cursor.fetchone()
        cursor.close()
        cache.setCachedMarketGroup(marketGroupID, row)
        return row

#------------------------------------------------------------------------------
SQL_MKTGRP_BY_PARENT = '''SELECT marketGroupID, marketGroupName, hasTypes
FROM invMarketGroups
WHERE parentGroupID = %s;'''
def getMarketGroupChildren(marketGroupID):
    try:
        return cache.getCachedMarketGroupChildren(marketGroupID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(SQL_MKTGRP_BY_PARENT, [marketGroupID])
        rows = cursor.fetchall()
        cursor.close()
        for row in rows:
            cache.setCachedMarketGroup(marketGroupID, row)
        cache.setCachedMarketGroupChildren(marketGroupID, rows)
        return rows

#------------------------------------------------------------------------------
SQL_ITEMS_BY_MKTGRP = 'SELECT * FROM invTypes WHERE marketGroupID = %s;'
def getMarketGroupItems(mktGroupID):
    cursor = EVE_DB.cursor()
    cursor.execute(SQL_MKTGRP_BY_PARENT, [mktGroupID])
    rows = cursor.fetchall()
    cursor.close()
    return rows

#------------------------------------------------------------------------------
SQL_ITEM = 'SELECT * FROM "invTypes" WHERE "typeID"=%s;'
def getItem(typeID):
    try:
        return cache.getCachedItem(typeID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(SQL_ITEM, [typeID])
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            raise ValueError('No item with typeID %d' % typeID)
        else:
            cache.setCachedItem(typeID, row)
            return row

#------------------------------------------------------------------------------
SQL_BLUEPRINT = 'SELECT * FROM invBlueprintTypes WHERE blueprintTypeID=%s;'
def getBlueprint(blueprintTypeID):
    try:
        return cache.getCachedBlueprint(blueprintTypeID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(SQL_BLUEPRINT, [blueprintTypeID])
        row = cursor.fetchone()
        cursor.close()
        if row is None:
            raise ValueError('No blueprint with blueprintTypeID %d' % blueprintTypeID)
        else:
            cache.setCachedBlueprint(blueprintTypeID, row)
            return row

#------------------------------------------------------------------------------
SQL_BP_ACTIVITIES = 'SELECT DISTINCT activityID FROM ramBlueprintReqs WHERE blueprintTypeID=%s;'
def getBpActivities(blueprintTypeID):
    try:
        return cache.getCachedBpActivities(blueprintTypeID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(SQL_BP_ACTIVITIES, [blueprintTypeID])
        rows = cursor.fetchall()
        cursor.close()
        cache.setCachedBpActivities(blueprintTypeID, rows)
        return rows
#------------------------------------------------------------------------------
SQL_ACTIVITY_REQS = '''SELECT requiredTypeID, quantity, damagePerJob, baseMaterial
FROM ramBlueprintReqs
WHERE blueprintTypeID=%s
  AND activityID=%s
  AND damagePerJob > 0.0 ORDER BY activityID;'''
def getActivityReqs(blueprintTypeID, activityID):
    try:
        return cache.getCachedActivityReqs(blueprintTypeID, activityID)
    except KeyError:
        cursor = EVE_DB.cursor()
        cursor.execute(SQL_ACTIVITY_REQS, [blueprintTypeID, activityID])
        rows = cursor.fetchall()
        cursor.close()
        cache.setCachedActivityReqs(blueprintTypeID, activityID, rows)
        return rows
#------------------------------------------------------------------------------
SQL_FUEL_CONSUMPTION = 'SELECT quantity FROM invControlTowerResources WHERE controlTowerTypeID = %s AND resourceTypeID = %s'
def getFuelConsumption(posItemID, fuelTypeID):
    cursor = EVE_DB.cursor()
    cursor.execute(SQL_FUEL_CONSUMPTION, [posItemID, fuelTypeID])
    row, = cursor.fetchone()
    cursor.close()
    return row
#------------------------------------------------------------------------------
SQL_SECURITY_STATUS = 'SELECT security FROM mapCelestialObjects WHERE itemID = %s'
def getSecurityStatus(systemID):
    cursor = EVE_DB.cursor()
    cursor.execute(SQL_SECURITY_STATUS, [systemID])
    row, = cursor.fetchone()
    cursor.close()
    return row

    