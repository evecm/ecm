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

__date__ = "2011 6 7"
__author__ = "diabeteman"


from django.db import connections

EVE_DB = connections['eve']

#------------------------------------------------------------------------------


class MarketGroup(object):
    
    BLUEPRINTS = 2
    SKILLS = 150
    SHIPS = 4
    ITEMS = 9
    
    def __init__(self, marketGroupID, marketGroupName, hasTypes):
        self.marketGroupID = marketGroupID
        self.marketGroupName = marketGroupName
        self.hasTypes = hasTypes
        self.children = []
    
    def __repr__(self):
        return '<MarketGroup: %s>' % (self.marketGroupName + ('*' if self.hasTypes else ''))  

#------------------------------------------------------------------------------
class Item(object):
    
    BLUEPRINT_CATID = 9
    SKILL_CATID = 16
    
    def __init__(self, typeID, typeName, techLevel=1, categoryID=0):
        self.typeID = typeID
        self.typeName = typeName
        self.techLevel = techLevel
        self.categoryID = categoryID
    
    def __repr__(self):
        return '<Item: %s>' % self.typeName

#------------------------------------------------------------------------------
class Blueprint(Item):
    
    def __init__(self, typeID, typeName, techLevel, productTypeID, productTypeName, productionTime, 
                 wasteFactor, batchSize, meLevel=0, peLevel=0):
        Item.__init__(self, typeID, typeName, techLevel, categoryID=Item.BLUEPRINT_CATID)
        self.productTypeID = productTypeID
        self.productTypeName = productTypeName
        self.productionTime = productionTime
        self.wasteFactor = wasteFactor
        self.batchSize = batchSize
        self.meLevel = meLevel
        self.peLevel = peLevel
        self.activities = []
    
    def calc_one_material(self, base):
        if self.meLevel < 0:
            value = base * (1.0 - ((self.meLevel - 1) * (self.wasteFactor * 0.01)));
        else:
            value = base * (1.0 + ((self.wasteFactor * 0.01) / (1.0 + self.meLevel)));
        return int(round(value))
    
    def __unicode__(self):
        return self.typeName
    
    def __repr__(self):
        return '<Blueprint: %s>' % self.typeName

#------------------------------------------------------------------------------
class BpActivity(object):
    
    MANUFACTURING = 1
    RESEARCH_PE = 3
    RESEARCH_ME = 4
    COPY = 5
    DUPLICATING = 6
    REVERSE_ENGINEERING = 7
    INVENTION = 8
    
    NAMES = {
        MANUFACTURING : "Manufacturing", 
        RESEARCH_PE : "Time Efficiency Research", 
        RESEARCH_ME : "Material Efficiency Research", 
        COPY : "Copying", 
        DUPLICATING : "Duplicating",
        REVERSE_ENGINEERING : "Reverse Engineering", 
        INVENTION : "Invention"
    }
    
    def __init__(self, activityID):
        self.activityID = activityID
        self.materials = []
    
    def __getattr__(self, attrName):
        if attrName == 'name':
            return BpActivity.NAMES[self.activityID]
        else:
            object.__getattribute__(self, attrName)
    
    def __cmp__(self, other):
        return cmp(self.activityID, other.activityID)
    
    def __unicode__(self):
        return BpActivity.NAMES[self.activityID]
    
    def __repr__(self):
        return '<BpActivity: %s>' % BpActivity.NAMES[self.activityID]

#------------------------------------------------------------------------------
class BpMaterial(Item):
    
    def __init__(self, typeID, typeName, quantity, damagePerJob=1.0):
        Item.__init__(self, typeID, typeName)
        self.quantity = quantity
        self.damagePerJob = damagePerJob
    
    
    
