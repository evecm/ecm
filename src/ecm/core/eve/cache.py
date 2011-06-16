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

__date__ = "2011 6 11"
__author__ = "diabeteman"

import threading

#------------------------------------------------------------------------------
CACHE_TYPENAMES = {}
LOCK_TYPENAMES = threading.RLock()
def getCachedTypeName(id):
    with LOCK_TYPENAMES: 
        return CACHE_TYPENAMES[id]
def setCachedTypeName(id, type):
    with LOCK_TYPENAMES: 
        CACHE_TYPENAMES[id] = type
#------------------------------------------------------------------------------
CACHE_LOCATIONS = {}
LOCK_LOCATIONS = threading.RLock()
def getCachedLocation(id):
    with LOCK_LOCATIONS: 
        return CACHE_LOCATIONS[id]
def setCachedLocation(id, name, security=0):
    with LOCK_LOCATIONS: 
        CACHE_LOCATIONS[id] = (name, security)

#------------------------------------------------------------------------------
CACHE_ITEMS = {}
LOCK_ITEMS = threading.RLock()
def getCachedItem(typeID):
    with LOCK_ITEMS: 
        return CACHE_ITEMS[typeID]
def setCachedItem(typeID, item):
    with LOCK_ITEMS: 
        CACHE_ITEMS[typeID] = item
    
#------------------------------------------------------------------------------
CACHE_BLUEPRINTS = {}
LOCK_BLUEPRINTS = threading.RLock()
def getCachedBlueprint(typeID):
    with LOCK_BLUEPRINTS: 
        return CACHE_BLUEPRINTS[typeID]
def setCachedBlueprint(typeID, bp):
    with LOCK_BLUEPRINTS: 
        CACHE_BLUEPRINTS[typeID] = bp

#------------------------------------------------------------------------------
CACHE_MKTGROUPS = {}
LOCK_MKTGROUPS = threading.RLock()
def getCachedMarketGroup(mktGroupID):
    with LOCK_MKTGROUPS: 
        return CACHE_MKTGROUPS[mktGroupID]
def setCachedMarketGroup(mktGroupID, mktGroup):
    with LOCK_MKTGROUPS: 
        CACHE_MKTGROUPS[mktGroupID] = mktGroup
#------------------------------------------------------------------------------
CACHE_MKTGROUP_CHILDREN = {}
LOCK_MKTGROUP_CHILDREN = threading.RLock()
def getCachedMarketGroupChildren(parentMktGroupID):
    with LOCK_MKTGROUP_CHILDREN: 
        return CACHE_MKTGROUP_CHILDREN[parentMktGroupID]
def setCachedMarketGroupChildren(parentMktGroupID, children):
    with LOCK_MKTGROUP_CHILDREN: 
        CACHE_MKTGROUP_CHILDREN[parentMktGroupID] = children
#------------------------------------------------------------------------------
CACHE_MKTGROUP_ITEMS = {}
LOCK_MKTGROUP_ITEMS = threading.RLock()
def getCachedMarketGroupItems(mktGroupID):
    with LOCK_MKTGROUP_ITEMS: 
        return CACHE_MKTGROUP_ITEMS[mktGroupID]
def setCachedMarketGroupItems(mktGroupID, items):
    with LOCK_MKTGROUP_ITEMS: 
        CACHE_MKTGROUP_ITEMS[mktGroupID] = items
#------------------------------------------------------------------------------
LOCK_SOLARSYSTEMS = threading.RLock()
CACHE_SOLARSYSTEMS = {}
def getCachedSolarSystemID(stationID):
    with LOCK_SOLARSYSTEMS: 
        return CACHE_SOLARSYSTEMS[stationID]
def setCachedSolarSystemID(stationID, solarSystemID):
    with LOCK_SOLARSYSTEMS: 
        CACHE_SOLARSYSTEMS[stationID] = solarSystemID

#------------------------------------------------------------------------------
LOCK_ACTIVITY_REQS = threading.RLock()
CACHE_ACTIVITY_REQS = {}
def getCachedActivityReqs(typeID, activityID):
    with LOCK_ACTIVITY_REQS: 
        return CACHE_ACTIVITY_REQS[(typeID, activityID)]
def setCachedActivityReqs(typeID, activityID, reqs):
    with LOCK_ACTIVITY_REQS: 
        CACHE_ACTIVITY_REQS[(typeID, activityID)] = reqs

#------------------------------------------------------------------------------
LOCK_BP_ACTIVITIES = threading.RLock()
CACHE_BP_ACTIVITIES = {}
def getCachedBpActivities(bpTypeID):
    with LOCK_BP_ACTIVITIES: 
        return CACHE_BP_ACTIVITIES[bpTypeID]
def setCachedBpActivities(bpTypeID, activities):
    with LOCK_BP_ACTIVITIES: 
        CACHE_BP_ACTIVITIES[bpTypeID] = activities

