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


from ecm.core.eve import db
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
    
    def __getattr__(self, attrName):
        if attrName == 'children':
            try:
                return self.__children
            except AttributeError:
                self.__children = [] 
                if self.hasTypes:
                    for row in db.getMarketGroupChildren(self.marketGroupID):
                        self.__children.append(MarketGroup(*row))
                else:
                    for row in db.getMarketGroupItems(self.marketGroupID):
                        self.__children.append(Item(*row))
                return self.__children
        else:
            return object.__getattribute__(self, attrName)
    
    @staticmethod
    def get(marketGroupID):
        return MarketGroup(*db.getMarketGroup(marketGroupID))
    
    def __repr__(self):
        return '<MarketGroup: %s>' % (self.marketGroupName + ('*' if self.hasTypes else ''))  

#------------------------------------------------------------------------------
class Item(object):
    
    BLUEPRINT_CATID = 9
    SKILL_CATID = 16
    def __init__(self, 
                 typeID,
                 groupID,
                 categoryID,
                 typeName,
                 blueprintTypeID,
                 techLevel,
                 description,
                 volume,
                 portionSize,
                 basePrice,
                 marketGroupID,
                 icon):
        self.typeID = typeID
        self.groupID = groupID
        self.categoryID = categoryID
        self.typeName = typeName
        self.blueprintTypeID = blueprintTypeID
        self.techLevel = techLevel
        self.description = description
        self.volume = volume
        self.portionSize = portionSize
        self.basePrice = basePrice
        self.marketGroupID = marketGroupID
        self.icon = icon
    
    def getBillOfMaterials(self, quantity=1.0, meLevel=0):
        bill = []
        try:
            materials = self.blueprint[BpActivity.MANUFACTURING].materials
            for m in materials:
                qty = quantity * apply_material_level(m.quantity, meLevel, self.blueprint.wasteFactor)
                bill.append(ActivityMaterial(m.requiredTypeID, qty, m.damagePerJob, m.baseMaterial))
        except NoBlueprintException:
            bill = []
        return bill
        
    def __getattr__(self, attrName):
        if attrName == 'blueprint':
            try:
                return self.__blueprint
            except AttributeError:
                if self.blueprintTypeID is None:
                    raise NoBlueprintException(self.typeID)
                else:
                    self.__blueprint = Blueprint(*db.getBlueprint(self.blueprintTypeID))
                    return self.__blueprint
        else:
            return object.__getattribute__(self, attrName)
    
    @staticmethod
    def get(typeID):
        return Item(*db.getItem(typeID=typeID))
    
    def __repr__(self):
        return '<Item: %s>' % self.typeName

#------------------------------------------------------------------------------
class Blueprint(object):
    
    def __init__(self, 
                 blueprintTypeID, 
                 parentBlueprintTypeID,
                 productTypeID,
                 productionTime,
                 techLevel,
                 researchProductivityTime,
                 researchMaterialTime,
                 researchCopyTime,
                 researcheTechTime,
                 productivityModifier,
                 materialModifier,
                 wasteFactor,
                 maxProductionLimit):
        self.blueprintTypeID = blueprintTypeID 
        self.parentBlueprintTypeID = parentBlueprintTypeID
        self.productTypeID = productTypeID
        self.productionTime = productionTime
        self.techLevel = techLevel
        self.researchProductivityTime = researchProductivityTime
        self.researchMaterialTime = researchMaterialTime
        self.researchCopyTime = researchCopyTime
        self.researcheTechTime = researcheTechTime
        self.productivityModifier = productivityModifier
        self.materialModifier = materialModifier
        self.wasteFactor = wasteFactor
        self.maxProductionLimit = maxProductionLimit
    

    
    def __getattr__(self, attrName):
        if attrName == 'activities':
            try:
                return self.__activities
            except AttributeError:
                self.__activities = {}
                for activityID, in db.getBpActivities(self.blueprintTypeID):
                    self.__activities[activityID] = BpActivity(self.blueprintTypeID, activityID)
                return self.__activities
        else:
            return object.__getattribute__(self, attrName)
    
    def __getitem__(self, activityID):
        try:
            return getattr(self, 'activities')[activityID]
        except KeyError:
            raise ValueError('Blueprint with blueprintTypeID=%d '
                             'has no activity with activityID=%s' 
                             % (self.blueprintTypeID, str(activityID)))
    
    @staticmethod
    def get(blueprintTypeID):
        return Blueprint(*db.getBlueprint(blueprintTypeID))
    
    def __unicode__(self):
        return 'Blueprint (blueprintTypeID=%d)' % self.blueprintTypeID
    
    def __repr__(self):
        return '<Blueprint: %d>' % self.blueprintTypeID

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
    
    def __init__(self, blueprintTypeID, activityID):
        self.blueprintTypeID = blueprintTypeID
        self.activityID = activityID
    
    def __getattr__(self, attrName):
        if attrName == 'name':
            return BpActivity.NAMES[self.activityID]
        elif attrName == 'materials':
            try:
                return self.__materials
            except AttributeError:
                self.__materials = []
                for req in db.getActivityReqs(self.blueprintTypeID, self.activityID):
                    self.__materials.append(ActivityMaterial(*req))
                return self.__materials
        else:
            return object.__getattribute__(self, attrName)
    
    def __cmp__(self, other):
        return cmp(self.blueprintTypeID, other.blueprintTypeID) or cmp(self.activityID, other.activityID)
    
    def __unicode__(self):
        return BpActivity.NAMES[self.activityID]
    
    def __repr__(self):
        return '<BpActivity: %s>' % BpActivity.NAMES[self.activityID]

#------------------------------------------------------------------------------
class ActivityMaterial(Item):
    
    def __init__(self, requiredTypeID, quantity, damagePerJob, baseMaterial):
        self.requiredTypeID = requiredTypeID
        self.quantity = quantity
        self.damagePerJob = damagePerJob
        self.baseMaterial = baseMaterial
    
    def __getattr__(self, attrName):
        try:
            try:
                return Item.__getattr__(self, attrName)
            except AttributeError:
                Item.__init__(self, *db.getItem(typeID=self.requiredTypeID))
                return Item.__getattr__(self, attrName)
        except AttributeError:
            return object.__getattribute__(self, attrName)

    def getBillOfMaterials(self, quantity=1.0, meLevel=0):
        bill = Item.getBillOfMaterials(self, quantity, meLevel)
        for m in bill: 
            m.quantity *= self.quantity
        return bill

    def __repr__(self):
        return '<ActivityMaterial: id=%d, qty=%d>' % (self.requiredTypeID, self.quantity)


#------------------------------------------------------------------------------
class NoBlueprintException(UserWarning):
    def __init__(self, typeID):
        self.typeID = typeID
    def __repr__(self):
        return 'NoBlueprintException: Item with typeID %d has no blueprint' % self.typeID
    def __str__(self):
        return 'Item with typeID %d has no blueprint' % self.typeID

#------------------------------------------------------------------------------
def apply_material_level(base, meLevel, wasteFactor, round=False):
    if meLevel < 0:
        value = base * (1.0 - ((meLevel - 1) * (wasteFactor * 0.01)));
    else:
        value = base * (1.0 + ((wasteFactor * 0.01) / (1.0 + meLevel)));
    if round:
        return int(round(value))
    else:
        return value
