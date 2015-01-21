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

__date__ = '2015 1 21'
__author__ = 'diabeteman'

from django.db import models

from ecm.utils.tools import cached_property
from ecm.apps.eve.formulas import apply_production_level, apply_material_level

#------------------------------------------------------------------------------
class Category(models.Model):

    class Meta:
        app_label = 'eve'
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
        app_label = 'eve'
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

    @property
    def categoryID(self):
        return self.category_id

    def __unicode__(self):
        return self.groupName

    def __eq__(self, other):
        return isinstance(other, Group) and other.groupID == self.groupID

    def __hash__(self):
        return self.groupID

#------------------------------------------------------------------------------
class ControlTowerResource(models.Model):

    class Meta:
        app_label = 'eve'
        get_latest_by = 'control_tower'
        ordering = ['control_tower', 'resource']
        unique_together = ('control_tower', 'resource')

    id = models.BigIntegerField(primary_key=True) #@ReservedAssignment
    control_tower = models.ForeignKey('Type', db_column='controlTowerTypeID',
                                      related_name='tower_resources_t')
    resource = models.ForeignKey('Type', db_column='resourceTypeID',
                                 related_name='tower_resources_r')
    purpose = models.SmallIntegerField()
    quantity = models.SmallIntegerField()
    minSecurityLevel = models.FloatField(null=True, blank=True)
    factionID = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return '%s: %d / hour' % (self.resource.typeName, self.quantity)

    def __eq__(self, other):
        return isinstance(other, ControlTowerResource) and other.id == self.id

    def __hash__(self):
        return self.id

#------------------------------------------------------------------------------
class MarketGroup(models.Model):

    class Meta:
        app_label = 'eve'
        get_latest_by = 'marketGroupID'
        ordering = ['marketGroupID']

    marketGroupID = models.IntegerField(primary_key=True)
    parent_group = models.ForeignKey('self', related_name='children_groups',
                                      db_column='parentGroupID', null=True, blank=True)
    marketGroupName = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    iconID = models.IntegerField(null=True, blank=True)
    hasTypes = models.SmallIntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.marketGroupName

    def __eq__(self, other):
        return isinstance(other, MarketGroup) and other.marketGroupID == self.marketGroupID

    def __hash__(self):
        return self.marketGroupID


#------------------------------------------------------------------------------
class BlueprintType(models.Model):

    class Meta:
        app_label = 'eve'
        get_latest_by = 'blueprintTypeID'
        ordering = ['blueprintTypeID']

    blueprintTypeID = models.IntegerField(primary_key=True)
    parent_blueprint = models.ForeignKey('self', related_name='children_blueprints',
                                         db_column='parentBlueprintTypeID', db_index=True,
                                         null=True, blank=True)
    product = models.OneToOneField('Type', db_column='productTypeID', db_index=True,
                                   null=True, blank=True)
    productionTime = models.IntegerField(null=True, blank=True)
    researchProductivityTime = models.IntegerField(null=True, blank=True)
    researchMaterialTime = models.IntegerField(null=True, blank=True)
    researchCopyTime = models.IntegerField(null=True, blank=True)
    inventionTime = models.IntegerField(null=True, blank=True)
    maxProductionLimit = models.IntegerField(null=True, blank=True)
    inventionBaseChance = models.FloatField(null=True, blank=True)
    __item = None

    def __getattr__(self, attr):
        try:
            # A BlueprintType is also a Type. We try to get attributes from the other class.
            if self.__item is None:
                self.__item = Type.objects.get(pk=self.blueprintTypeID)
            return getattr(self.__item, attr)
        except AttributeError:
            return models.Model.__getattribute__(self, attr)

    @property
    def parentBlueprintTypeID(self):
        return self.parent_blueprint_id

    @property
    def productTypeID(self):
        return self.product_id

    @cached_property
    def activities(self):
        acts = []
        for act_id in set(self.requirements.values_list('activityID', flat=True)):
            acts.append(BlueprintType.Activity(activityID=act_id))
        acts.sort()
        return acts

    def materials(self, activityID):
        return self.requirements.select_related(depth=2).filter(activityID=activityID)

    def get_duration(self, activity, runs=1, pe_level=0):
        """
        Calculate the duration (in seconds) needed to perform the specified activity.
        """
        if activity == BlueprintType.Activity.MANUFACTURING:
            return apply_production_level(runs * self.productionTime, pe_level)
        elif activity == BlueprintType.Activity.INVENTION:
            return runs * self.inventionTime
        elif activity == BlueprintType.Activity.RESEARCH_ME:
            return runs * self.researchMaterialTime
        elif activity == BlueprintType.Activity.RESEARCH_PE:
            return runs * self.researchProductivityTime
        elif activity == BlueprintType.Activity.COPY:
            return runs * self.researchCopyTime
        else:
            return 0

    def get_involved_blueprints(self, recurse=False):
        blueprints = set()
        for mat in self.materials(BlueprintType.Activity.MANUFACTURING):
            mat_blueprint = mat.required_type.blueprint
            if mat_blueprint is not None:
                blueprints.add(mat_blueprint)
                if recurse:
                    blueprints.update(mat_blueprint.get_involved_blueprints(recurse=True))
        return blueprints

    def get_bill_of_materials(self, activity, runs, me_level, round_result=False):
        """
        Resolve the materials needed for the specified activity.
        Quantities are given as floats (to be rounded).
        """
        rounded_runs = int(round(runs))
        materials = []

        for mat in self.materials(activity):
            mat.quantity = apply_material_level(mat.quantity,
                                                me_level,
                                                round_result)
            mat.quantity *= rounded_runs
            materials.append(mat)
        return materials

    def __unicode__(self):
        return self.typeName

    def __eq__(self, other):
        return isinstance(other, BlueprintType) and other.blueprintTypeID == self.blueprintTypeID

    def __hash__(self):
        return self.blueprintTypeID

    class Activity(object):

        MANUFACTURING = 1
        RESEARCH_PE = 3
        RESEARCH_ME = 4
        COPY = 5
        DUPLICATING = 6
        REVERSE_ENGINEERING = 7
        INVENTION = 8

        NAMES = {
            MANUFACTURING : 'Manufacturing',
            RESEARCH_PE : 'Time Efficiency Research',
            RESEARCH_ME : 'Material Efficiency Research',
            COPY : 'Copying',
            DUPLICATING : 'Duplicating',
            REVERSE_ENGINEERING : 'Reverse Engineering',
            INVENTION : 'Invention'
        }

        def __init__(self, activityID):
            self.activityID = activityID

        @property
        def name(self):
            return self.NAMES[self.activityID]

        def __unicode__(self):
            return unicode(self.name)

        def __cmp__(self, other):
            return cmp(self.activityID, other.activityID)

#------------------------------------------------------------------------------
class BlueprintReq(models.Model):
    """
    A material involved in the "execution" of a BpActivity.
    Can be a raw material, manufactured item, skill, datacore, etc.
    """

    class Meta:
        app_label = 'eve'
        ordering = ['blueprint', 'activityID', 'required_type']

    id = models.BigIntegerField(primary_key=True) #@ReservedAssignment
    blueprint = models.ForeignKey('BlueprintType', db_column='blueprintTypeID',
                                  related_name='requirements')
    activityID = models.SmallIntegerField(default=BlueprintType.Activity.MANUFACTURING,
                                          choices=BlueprintType.Activity.NAMES.items())
    required_type = models.ForeignKey('Type', db_column='requiredTypeID')
    quantity = models.IntegerField(default=0)
    __item = None

    @property
    def blueprintTypeID(self):
        return self.blueprint_id

    @property
    def requiredTypeID(self):
        return self.required_type_id

    def __getattr__(self, attr):
        #prevent endless recursion
        if attr not in ('required_type','_required_type_cache'):
            try:
                getattr(self.required_type, attr)
            except AttributeError:
                return models.Model.__getattribute__(self, attr)
        else:
            return models.Model.__getattribute__(self, attr)

    def __unicode__(self):
        return '%s x%d' % (self.required_type, self.quantity)

    def __eq__(self, other):
        return isinstance(other, BlueprintReq) and other.id == self.id

    def __hash__(self):
        return self.id




#------------------------------------------------------------------------------
class Type(models.Model):

    class Meta:
        app_label = 'eve'
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
    description = models.TextField(null=True, blank=True)
    volume = models.FloatField(null=True, blank=True)
    portionSize = models.IntegerField(null=True, blank=True)
    raceID = models.SmallIntegerField(null=True, blank=True)
    basePrice = models.FloatField(null=True, blank=True)
    market_group = models.ForeignKey('MarketGroup', related_name='items',
                                     db_column='marketGroupID',
                                     null=True, blank=True, db_index=True)
    metaGroupID = models.SmallIntegerField(null=True, blank=True)
    published = models.SmallIntegerField(null=True, blank=True, db_index=True)

    @property
    def blueprintTypeID(self):
        return self.blueprint_id

    @property
    def groupID(self):
        return self.group_id

    @property
    def categoryID(self):
        return self.category_id

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
        app_label = 'eve'
        get_latest_by = 'itemID'
        ordering = ['itemID']

    itemID = models.IntegerField(primary_key=True)
    type = models.ForeignKey('Type', db_column='typeID') #@ReservedAssignment
    group =  models.ForeignKey('Group', db_column='groupID', db_index=True, null=True, blank=True)
    solarSystemID = models.IntegerField(db_index=True, null=True, blank=True)
    regionID = models.IntegerField(db_index=True, null=True, blank=True)
    itemName = models.CharField(max_length=100, null=True, blank=True)
    security = models.FloatField(null=True, blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)

    @property
    def typeID(self):
        return self.type_id

    @property
    def groupID(self):
        return self.group_id

    def __unicode__(self):
        return self.itemName

    def __eq__(self, other):
        return isinstance(other, CelestialObject) and other.itemID == self.itemID

    def __hash__(self):
        return self.itemID

#------------------------------------------------------------------------------
class SkillReq(models.Model):
    
    class Meta:
        app_label = 'eve'
        ordering = ['item', 'skill']
    
    # we must add a forged primary key because django doesn't support multi-column primary keys
    id = models.BigIntegerField(primary_key=True)   #@ReservedAssignment
    item = models.ForeignKey('Type', related_name='skill_reqs')
    skill = models.ForeignKey('Type', related_name='+')
    required_level = models.SmallIntegerField()

    def __unicode__(self):
        return u"%s -> %s = %d" % (self.item.typeName, self.skill.typeName, self.required_level) 

    def __hash__(self):
        return self.id
    
    def __eq__(self, other):
        return isinstance(other, SkillReq) and other.id == self.id

