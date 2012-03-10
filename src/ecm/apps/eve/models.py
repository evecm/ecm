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

__date__ = '2012 3 6'
__author__ = 'diabeteman'

from django.db import models

from ecm.core.utils import cached_property
from ecm.apps.eve.formulas import apply_production_level, apply_material_level

#------------------------------------------------------------------------------
class Category(models.Model):
    
    class Meta:
        db_table = 'invCategories'
        managed = False
        get_latest_by = 'categoryID'
        ordering = ['categoryID']
    
    categoryID = models.IntegerField(primary_key=True)
    categoryName = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    iconID = models.IntegerField(null=True, blank=True)
    published = models.SmallIntegerField(null=True, blank=True, db_index=True)
    
    def __unicode__(self):
        return self.categoryName
    
    def __eq__(self, other):
        return isinstance(other, Category) and other.categoryID == self.categoryID
    
    def __hash__(self):
        return self.categoryID
    
#------------------------------------------------------------------------------ 
class Group(models.Model):
    
    class Meta:
        db_table = 'invGroups'
        managed = False
        get_latest_by = 'groupID'
        ordering = ['groupID']
    
    groupID =  models.IntegerField(primary_key=True)
    category =  models.ForeignKey('Category', db_column='categoryID', 
                                  related_name='groups')
    groupName =  models.CharField(max_length=100)
    description =  models.TextField(null=True, blank=True)
    iconID =  models.IntegerField(null=True, blank=True)
    useBasePrice =  models.SmallIntegerField(null=True, blank=True)
    allowManufacture =  models.SmallIntegerField(null=True, blank=True)
    allowRecycler =  models.SmallIntegerField(null=True, blank=True)
    anchored =  models.SmallIntegerField(null=True, blank=True)
    anchorable =  models.SmallIntegerField(null=True, blank=True)
    fittableNonSingleton =  models.SmallIntegerField(null=True, blank=True)
    published =  models.SmallIntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.groupName
    
    def __eq__(self, other):
        return isinstance(other, Group) and other.groupID == self.groupID
    
    def __hash__(self):
        return self.groupID

#------------------------------------------------------------------------------
class ControlTowerResource(models.Model):
    
    class Meta:
        db_table = 'invControlTowerResources'
        managed = False
        get_latest_by = 'control_tower'
        ordering = ['control_tower', 'resource']
        unique_together = ('control_tower', 'resource')
    
    control_tower = models.ForeignKey('Type', db_column='controlTowerTypeID', 
                                      related_name='tower_resources_t', primary_key=True)
    resource = models.ForeignKey('Type', db_column='resourceTypeID', 
                                 related_name='tower_resources_r')
    purpose = models.SmallIntegerField()
    quantity = models.SmallIntegerField()
    minSecurityLevel = models.FloatField()
    factionID = models.SmallIntegerField()
    
    def __unicode__(self):
        return '%s: %d / hour' % (self.resource.typeName, self.quantity)
    
    def __eq__(self, other):
        return (isinstance(other, ControlTowerResource) 
                and other.controlTowerTypeID == self.controlTowerTypeID
                and other.resourceTypeID == self.resourceTypeID)
    
    def __hash__(self):
        return self.controlTowerTypeID * 1000000 + self.resourceTypeID

#------------------------------------------------------------------------------
class MarketGroup(models.Model):
    
    class Meta:
        db_table = 'invMarketGroups'
        managed = False
        get_latest_by = 'marketGroupID'
        ordering = ['marketGroupID']
        
    marketGroupID = models.IntegerField(primary_key=True)
    parent_group = models.ForeignKey('self', related_name='children_groups', 
                                      db_column='parentGroupID', null=True, blank=True)
    marketGroupName = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    iconID = models.SmallIntegerField(null=True, blank=True)
    hasTypes = models.SmallIntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return self.marketGroupName
    
    def __eq__(self, other):
        return isinstance(other, MarketGroup) and other.marketGroupID == self.marketGroupID
    
    def __hash__(self):
        return self.marketGroupID
    
#------------------------------------------------------------------------------
class BlueprintReq(models.Model):
    """
    A material involved in the "execution" of a BpActivity.
    Can be a raw material, manufactured item, skill, datacore, etc.
    """
    
    class Meta:
        db_table = 'ramBlueprintReqs'
        managed = False
        ordering = ['blueprint', 'activityID', 'required_type']
        unique_together = ('blueprint', 'activityID', 'required_type')
    
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
    
    blueprint = models.ForeignKey('BlueprintType', db_column='blueprintTypeID', 
                                  related_name='requirements', primary_key=True)
    activityID = models.SmallIntegerField(default=MANUFACTURING, choices=NAMES.items())
    required_type = models.ForeignKey('Type', db_column='requiredTypeID')
    quantity = models.IntegerField(default=0)
    damagePerJob = models.FloatField(default=1.0)
    baseMaterial = models.IntegerField(default=0)
    __item = None
    
    def __getattr__(self, attr):
        try:
            getattr(self.required_type, attr)
        except AttributeError:
            return models.Model.__getattribute__(self, attr)
    
    
    def __unicode__(self):
        return '%s x%d' % (self.required_type, self.quantity)
    
    def __eq__(self, other):
        return (isinstance(other, BlueprintReq) 
                and other.blueprintTypeID == self.blueprintTypeID
                and other.activityID == self.activityID
                and other.requiredTypeID == self.requiredTypeID)
    
    def __hash__(self):
        return self.blueprintTypeID * 100000000 + self.requiredTypeID * 10 + self.activityID
    
    
#------------------------------------------------------------------------------
class BlueprintType(models.Model):
    
    class Meta:
        db_table = 'invBlueprintTypes'
        managed = False
        get_latest_by = 'blueprintTypeID'
        ordering = ['blueprintTypeID']
    
    blueprintTypeID = models.IntegerField(primary_key=True)
    parent_blueprint = models.ForeignKey('self', related_name='children_blueprints',
                                         db_column='parentBlueprintTypeID', db_index=True, 
                                         null=True, blank=True)
    product = models.OneToOneField('Type', db_column='productTypeID', db_index=True, 
                                   null=True, blank=True)
    productionTime = models.IntegerField(null=True, blank=True)
    techLevel = models.SmallIntegerField(null=True, blank=True)
    data_interface = models.ForeignKey('Type', db_index=True, db_column='dataInterfaceID', 
                                       null=True, blank=True, 
                                       related_name='blueprint_datainterfaces')
    researchProductivityTime = models.IntegerField(null=True, blank=True)
    researchMaterialTime = models.IntegerField(null=True, blank=True)
    researchCopyTime = models.IntegerField(null=True, blank=True)
    researchTechTime = models.IntegerField(null=True, blank=True)
    productivityModifier = models.IntegerField(null=True, blank=True)
    materialModifier = models.SmallIntegerField(null=True, blank=True)
    wasteFactor = models.SmallIntegerField(null=True, blank=True)
    maxProductionLimit = models.IntegerField(null=True, blank=True)
    __item = None
    
    def __getattr__(self, attr):
        try:
            # A BlueprintType is also a Type. We try to get attributes from the other class.
            if self.__item is None:
                self.__item = Type.objects.get(pk=self.blueprintTypeID)
            return getattr(self.__item, attr)
        except AttributeError:
            return models.Model.__getattribute__(self, attr)
    
    @cached_property
    def activities(self):
        return self.requirements.values_list('activityID', flat=True).distinct()
    
    def materials(self, activityID):
        return self.requirements.select_related(depth=2).filter(activityID=activityID)
    
    def get_duration(self, activity, runs=1, pe_level=0):
        """
        Calculate the duration (in seconds) needed to perform the specified activity.
        """
        if activity == BlueprintReq.MANUFACTURING:
            return apply_production_level(runs * self.productionTime, pe_level,
                                          self.productivityModifier)
        elif activity == BlueprintReq.INVENTION:
            return runs * self.researchTechTime
        elif activity == BlueprintReq.RESEARCH_ME:
            return runs * self.researchMaterialTime
        elif activity == BlueprintReq.RESEARCH_PE:
            return runs * self.researchProductivityTime
        elif activity == BlueprintReq.COPY:
            return runs * self.researchCopyTime
        else:
            return 0
    
    def get_involved_blueprints(self, recurse=False):
        blueprints = set()
        for mat in self.materials(BlueprintReq.MANUFACTURING):
            if mat.blueprint is not None:
                blueprints.add(mat.blueprint)
                if recurse:
                    blueprints.update(mat.blueprint.get_involved_blueprints(recurse=True))
        return blueprints
    
    def get_bill_of_materials(self, activity, runs, me_level, round_result=False):
        """
        Resolve the materials needed for the specified activity.
        Quantities are given as floats (to be rounded).
        """
        bill = []
        rounded_runs = int(round(runs))
        materials = self.materials(activity)
        for mat in materials:
            if mat.damagePerJob > 0:
                mat.quantity *= rounded_runs
                if mat.baseMaterial > 0:
                    mat.quantity = apply_material_level(mat.quantity, me_level, 
                                                        self.wasteFactor, round_result)
                bill.append(mat)
        return bill
    
    def __unicode__(self):
        return self.item.typeName
    
    def __eq__(self, other):
        return isinstance(other, BlueprintType) and other.blueprintTypeID == self.blueprintTypeID
    
    def __hash__(self):
        return self.blueprintTypeID

#------------------------------------------------------------------------------
class Type(models.Model):
    
    class Meta:
        db_table = 'invTypes'
        managed = False
        get_latest_by = 'typeID'
        ordering = ['typeID']
    
    typeID = models.IntegerField(primary_key=True)
    group =  models.ForeignKey('Group', db_column='groupID', 
                               related_name='types', db_index=True)
    category =  models.ForeignKey('Category', db_column='categoryID', 
                                  related_name='types', db_index=True)
    typeName = models.CharField(max_length=100, null=True, blank=True)
    blueprint = models.OneToOneField('BlueprintType', db_column='blueprintTypeID', 
                                     null=True, blank=True)
    techLevel = models.SmallIntegerField(null=True, blank=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    portionSize = models.IntegerField(null=True, blank=True)
    raceID = models.SmallIntegerField(null=True, blank=True)
    basePrice = models.FloatField(null=True, blank=True)
    market_group = models.ForeignKey('MarketGroup', related_name='items', 
                                     db_column='marketGroupID', 
                                     null=True, blank=True, db_index=True)
    metaGroupID = models.SmallIntegerField(null=True, blank=True)
    icon = models.CharField(max_length=32, null=True, blank=True)
    published = models.SmallIntegerField(null=True, blank=True, db_index=True)
    
    def __unicode__(self):
        return self.typeName
    
    def __eq__(self, other):
        return isinstance(other, Type) and other.typeID == self.typeID
    
    def __hash__(self):
        return self.typeID


    class NoBlueprintException(UserWarning):

        def __init__(self, typeID):
            self.typeID = typeID
    
        def __repr__(self):
            return '<%s: %s>' % (self.__class__.__name__, str(self))
    
        def __str__(self):
            return 'Item with typeID %s has no blueprint' % str(self.typeID)


#------------------------------------------------------------------------------
class CelestialObject(models.Model):
    
    class Meta:
        db_table = 'mapCelestialObjects'
        managed = False
        get_latest_by = 'itemID'
        ordering = ['itemID']
    
    itemID = models.IntegerField(primary_key=True)
    type = models.ForeignKey('Type', db_column='typeID') #@ReservedAssignment
    group =  models.ForeignKey('Group', db_column='groupID', db_index=True)
    solarSystemID = models.IntegerField(db_index=True)
    regionID = models.IntegerField(db_index=True)
    itemName = models.CharField(max_length=100)
    security = models.FloatField(null=True, blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    
    def __unicode__(self):
        return self.itemName
    
    def __eq__(self, other):
        return isinstance(other, CelestialObject) and other.itemID == self.itemID
    
    def __hash__(self):
        return self.itemID

