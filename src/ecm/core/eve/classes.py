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
from ecm.core.utils import cached_property

#------------------------------------------------------------------------------
class MarketGroup(object):
    """
    Represents a market group from EVE's item database.
    Only convenient for item browsing.
    """

    BLUEPRINTS = 2
    SKILLS = 150
    SHIPS = 4
    ITEMS = 9

    def __init__(self, marketGroupID, marketGroupName, hasTypes):
        self.marketGroupID = marketGroupID
        self.marketGroupName = marketGroupName
        self.hasTypes = hasTypes
        self.__children = None # lazy attribute

    def __getattr__(self, attrName):
        """
        Lazy attributes are handled here.
        """
        if attrName == 'children':
            if self.__children is not None:
                return self.__children
            else:
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
        """
        Static method for instanciating a MarketGroup from a marketGroupID
        """
        return MarketGroup(*db.getMarketGroup(marketGroupID))

    def __repr__(self):
        return '<MarketGroup: %s>' % (self.marketGroupName + ('*' if self.hasTypes else ''))

    def __eq__(self, other):
        return isinstance(other, MarketGroup) and self.marketGroupID == other.marketGroupID

    def __hash__(self):
        return self.marketGroupID

#------------------------------------------------------------------------------
class Item(object):
    """
    An item from EVE database.
    """

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
                 raceID,
                 basePrice,
                 marketGroupID,
                 icon,
                 published):
        self.typeID = typeID
        self.groupID = groupID
        self.categoryID = categoryID
        self.typeName = typeName
        self.blueprintTypeID = blueprintTypeID
        self.techLevel = techLevel
        self.description = description
        self.volume = volume
        self.portionSize = portionSize
        self.raceID = raceID
        self.basePrice = basePrice
        self.marketGroupID = marketGroupID
        self.icon = icon
        self.published = published

    @cached_property
    def blueprint(self):
        if self.blueprintTypeID is None:
            # Item cannot be manufactured nor invented.
            raise NoBlueprintException(self.typeID)
        else:
            return Blueprint.new(self.blueprintTypeID)

    def __repr__(self):
        return '<Item: %s>' % self.typeName

    def __eq__(self, other):
        return isinstance(other, Item) and self.typeID == other.typeID

    def __hash__(self):
        return self.typeID

    @staticmethod
    def new(typeID):
        """
        Static method for instanciating an Item from a typeID
        """
        return Item(*db.getItem(typeID=typeID))

#------------------------------------------------------------------------------
class Blueprint(Item):

    def __init__(self,
                 typeID,
                 parentBlueprintTypeID,
                 productTypeID,
                 productionTime,
                 techLevel,
                 dataInterfaceID,
                 researchProductivityTime,
                 researchMaterialTime,
                 researchCopyTime,
                 researchTechTime,
                 productivityModifier,
                 materialModifier,
                 wasteFactor,
                 maxProductionLimit):
        self.typeID = typeID
        self.parentBlueprintTypeID = parentBlueprintTypeID
        self.productTypeID = productTypeID
        self.productionTime = productionTime
        self.techLevel = techLevel
        self.dataInterfaceID = dataInterfaceID
        self.researchProductivityTime = researchProductivityTime
        self.researchMaterialTime = researchMaterialTime
        self.researchCopyTime = researchCopyTime
        self.researchTechTime = researchTechTime
        self.productivityModifier = productivityModifier
        self.materialModifier = materialModifier
        self.wasteFactor = wasteFactor
        self.maxProductionLimit = maxProductionLimit

    @cached_property
    def activities(self):
        activities = {}
        for activityID, in db.getBpActivities(self.typeID):
            activities[activityID] = BpActivity(self.typeID, activityID)
        return activities

    @cached_property
    def item(self):
        return Item.new(self.productTypeID)

    @cached_property
    def parentBlueprint(self):
        if self.parentBlueprintTypeID is None:
            raise NoParentBlueprintException(self.typeID)
        else:
            return Blueprint.new(self.parentBlueprintTypeID)

    def getInvolvedBlueprints(self, recurse=False):
        blueprints = set()
        for mat in self[BpActivity.MANUFACTURING].materials:
            if mat.blueprintTypeID is not None:
                blueprints.add(mat.blueprint)
                if recurse:
                    blueprints.update(mat.blueprint.getInvolvedBlueprints(recurse=True))
        return blueprints

    def getBillOfMaterials(self, runs, meLevel, activity, round_result=False):
        """
        Resolve the materials needed for the specified activity.
        Quantities are given as floats (to be rounded).
        """
        bill = []
        roundedRuns = int(round(runs))
        materials = self[activity].materials
        for m in materials:
            if m.damagePerJob > 0:
                qty = roundedRuns * m.quantity
                if m.baseMaterial > 0:
                    qty = apply_material_level(qty, meLevel, self.wasteFactor, round_result)
                bill.append(ActivityMaterial(m.requiredTypeID, qty, m.damagePerJob, m.baseMaterial))
        return bill

    def getDuration(self, runs, peLevel, activity):
        """
        Calculate the duration (in seconds) needed to perform the specified activity.
        """
        if activity == BpActivity.MANUFACTURING:
            return apply_production_level(runs * self.productionTime, peLevel)
        elif activity == BpActivity.INVENTION:
            return runs * self.researchTechTime
        else:
            return 0


    def __getattr__(self, attrName):
        """
        Lazy attributes are handled here.
        """
        try:
            try:
                return Item.__getattr__(self, attrName)
            except AttributeError:
                # a Blueprint is also an Item. Item's constructor is only called if needed.
                Item.__init__(self, *db.getItem(typeID=self.typeID))
                return Item.__getattr__(self, attrName)
        except AttributeError:
            return object.__getattribute__(self, attrName)

    def __getitem__(self, activityID):
        try:
            return self.activities[activityID]
        except KeyError:
            raise KeyError('Blueprint with blueprintTypeID=%s '
                             'has no activity with activityID=%s'
                             % (str(self.blueprintTypeID), str(activityID)))

    def __hash__(self):
        return self.typeID

    def __eq__(self, other):
        return isinstance(other, Blueprint) and self.typeID == other.typeID

    def __unicode__(self):
        return self.typeName

    def __repr__(self):
        return '<Blueprint: %s>' % self.typeName

    @staticmethod
    def new(typeID):
        """
        Static method for instanciating a Blueprint from its typeID
        """
        return Blueprint(*db.getBlueprint(typeID))

#------------------------------------------------------------------------------
class BpActivity(object):
    """
    An activity that can be performed on a blueprint.
    Such as Manufacturing, Invention, etc.
    """

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

    @cached_property
    def name(self):
        try:
            return BpActivity.NAMES[self.activityID]
        except KeyError:
            return 'Unknown Activity ID: %s' % str(self.activityID)

    @cached_property
    def materials(self):
        materials = []
        for req in db.getActivityReqs(self.blueprintTypeID, self.activityID):
            materials.append(ActivityMaterial(*req))
        return materials

    def __cmp__(self, other):
        return cmp(self.blueprintTypeID, other.blueprintTypeID) or cmp(self.activityID, other.activityID)

    def __unicode__(self):
        return BpActivity.NAMES[self.activityID]

    def __repr__(self):
        return '<BpActivity: %s>' % BpActivity.NAMES[self.activityID]

    def __eq__(self, other):
        return isinstance(other, BpActivity) and hash(self) == hash(other)

    def __hash__(self):
        return self.activityID * 1000000 + self.blueprintTypeID


#------------------------------------------------------------------------------
class ActivityMaterial(Item):
    """
    A material involved in the "execution" of a BpActivity.
    Can be a raw material, manufactured item, skill, datacore, etc.
    """

    def __init__(self, requiredTypeID, quantity, damagePerJob, baseMaterial):
        self.requiredTypeID = requiredTypeID
        self.quantity = quantity
        self.damagePerJob = damagePerJob
        self.baseMaterial = baseMaterial

    def __getattr__(self, attrName):
        """
        Lazy attributes are handled here.
        """
        try:
            try:
                return Item.__getattr__(self, attrName)
            except AttributeError:
                # an ActivityMaterial is also an Item.
                # Item's constructor is only called if needed.
                Item.__init__(self, *db.getItem(typeID=self.requiredTypeID))
                return Item.__getattr__(self, attrName)
        except AttributeError:
            return object.__getattribute__(self, attrName)

    def __repr__(self):
        return '<ActivityMaterial: id=%d, qty=%d>' % (self.requiredTypeID, self.quantity)


#------------------------------------------------------------------------------
class NoBlueprintException(UserWarning):

    def __init__(self, typeID):
        self.typeID = typeID

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))

    def __str__(self):
        return 'Item with typeID %s has no blueprint' % str(self.typeID)

#------------------------------------------------------------------------------
class NoParentBlueprintException(NoBlueprintException):

    def __str__(self):
        return 'Blueprint with id %s has no parent blueprint' % str(self.typeID)

#------------------------------------------------------------------------------
def apply_material_level(base, meLevel, wasteFactor, round_result=False):
    """
    Calculate the quantity needed for a material
    considering the waste factor and the material efficiency of the blueprint involved.
    """
    if meLevel < 0:
        value = base * (1.0 - ((meLevel - 1) * (wasteFactor * 0.01)));
    else:
        value = base * (1.0 + ((wasteFactor * 0.01) / (1.0 + meLevel)));
    if round_result:
        return int(round(value))
    else:
        return value

#------------------------------------------------------------------------------
def apply_production_level(base, peLevel, round_result=False):
    """
    Calculate the duration (in seconds) needed for the manufacturing of an item
    considering the production efficiency of the item's blueprint.
    """
    baseTime = 0.8 * base # we consider the industry skill is at level 5
    if peLevel >= 0:
        value = baseTime * (1.0 - (0.2 * (peLevel / (1.0 + peLevel))))
    else:
        value = baseTime * (1.0 - 0.1 * peLevel)
    if round_result:
        return int(round(value))
    else:
        return value
