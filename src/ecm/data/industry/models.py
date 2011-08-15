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

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from ecm.core.eve.classes import Item, Blueprint, NoBlueprintException
from ecm.core.eve import db, constants

#------------------------------------------------------------------------------
class MileStone(models.Model):
    """
    To simulate a Tailor-like process, 
    jobs are affected to MileStones which are 'fixed periodic delivery dates'.
    """
    date = models.DateField(unique=True)
    
    def next(self):
        next_date = self.date + timedelta(days=settings.MILESTONE_INTERVAL_DAYS)
        return MileStone.objects.get_or_create(date=next_date)
    
    def prev(self):
        prev_date = self.date - timedelta(days=settings.MILESTONE_INTERVAL_DAYS)
        return MileStone.objects.get_or_create(date=prev_date)

#------------------------------------------------------------------------------
class Order(models.Model):
    """
    An order submitted by a User or the application.
    each order must follow the same life cycle specified by the VALID_TRANSITIONS hash table.
    An order can contain multiple rows (one for each different item)
    """

    # states
    DRAFT = 0
    PENDING = 1
    PROBLEMATIC = 2
    ACCEPTED = 3
    PLANNED = 4
    IN_PREPARATION = 5
    READY = 6
    DELIVERED = 7
    PAID = 8
    CANCELED = 9
    REJECTED = 10
    
    # states text
    STATES_CHOICES = (
        (DRAFT,             _('Draft')),
        (PENDING,           _('Pending')),
        (PROBLEMATIC,       _('Problematic')),
        (ACCEPTED,          _('Accepted')),
        (PLANNED,           _('Planned')),
        (IN_PREPARATION,    _('In Preparation')),
        (READY,             _('Ready')),
        (DELIVERED,         _('Delivered')),
        (PAID,              _('Paid')),
        (CANCELED,          _('Canceled by Client')),
        (REJECTED,          _('Rejected by Manufacturer')),
    )
    
    # allowed transitions between states
    VALID_TRANSITIONS = {
        DRAFT : (DRAFT, PENDING, CANCELED),
        PENDING : (DRAFT, PROBLEMATIC, ACCEPTED, CANCELED, REJECTED),
        ACCEPTED : (PLANNED, IN_PREPARATION, CANCELED),
        PLANNED : (IN_PREPARATION, CANCELED),
        IN_PREPARATION : (READY, CANCELED),
        READY : (DELIVERED, CANCELED),
        DELIVERED : (PAID, CANCELED),
        PAID : (),
        CANCELED : (),
        REJECTED : (),
    }
    
    originator = models.ForeignKey(User, related_name='orders_created')
    manufacturer = models.ForeignKey(User, null=True, blank=True, related_name='orders_manufactured')
    deliveryMan = models.ForeignKey(User, null=True, blank=True, related_name='orders_delivered')
    client = models.CharField(max_length=255, null=True, blank=True)
    deliveryLocation = models.CharField(max_length=255, null=True, blank=True)
    mileStone = models.ForeignKey(MileStone, related_name='orders', null=True, blank=True)
    state = models.PositiveIntegerField(default=DRAFT, choices=STATES_CHOICES)
    discount = models.FloatField(default=0.0)
    quote = models.FloatField(null=True, blank=True)
    
    #############################
    # TRANSISTIONS
    
    def addComment(self, user, comment):
        self.logs.add(state=self.state, user=user, text=str(comment))
    
    def changeState(self, newState, user, comment):
        """
        Modify the state of an order. Adding a comment in the order logs.
        
        Checks if the new state is allowed in the life cycle. If not, raises an IllegalStateError
        """
        if newState not in Order.VALID_TRANSITIONS[newState]:
            legalStates = str([ Order.STATES[s] for s in Order.VALID_TRANSITIONS[newState] ])
            raise IllegalStateError(Order.STATES[newState]+' is illegal. Only '+legalStates+' are allowed.')
        else:
            self.state = newState
            self.addComment(user, comment)
    
    def modify(self, newItems):
        """
        Modification of the order. 
        An order can only be modified if its state is DRAFT or PENDING.
        
        newItems must be a list of tuples such as :
        [(itemID_A, qty_A), (itemID_B, qty_B), (itemID_C, qty_C)]
        """
        if self.rows.all() or self.logs.all():
            comment = "Order modified by originator."
        else:
            comment = "Order created."
        self.changeState(Order.DRAFT, self.originator, comment)
        self.rows.clear()
        for itemID, quantity in newItems:
            self.rows.add(itemID=itemID, quantity=quantity)
        self.save()
    
    def confirm(self):
        """
        Originator's confirmation of the order. Warns the manufacturing team. 
        """
        self.changeState(Order.PENDING, self.originator, "Order confirmed by originator.")
        self.save()
        # TODO: handle the alerts
    
    def accept(self, manufacturer):
        """
        Acceptation by a manufacturer.
        The order cannot be modified by its originator after acceptation.
        
        During the "accept" transition, we check if the order can be fulfilled.
        If it can, its states changes to ACCEPTED. If not, the order changes to PROBLEMATIC.
        """
        try:
            self.checkIfCanBeFulfilled()
            self.createJobs()
            self.changeState(Order.ACCEPTED, user=manufacturer, comment="Order accepted")
        except OrderCannotBeFulfilled as err:
            self.changeState(Order.PROBLEMATIC, user=manufacturer, comment=str(err)) 
            
    def resolve(self, manufacturer, comment):
        """
        Resolution of a problematic order.
        
        This is a manual operation and entering a comment is mandatory to explain 
        why the order was accepted despite the fact that is was PROBLEMATIC
        """
        self.createJobs()
        self.changeState(Order.ACCEPTED, manufacturer, comment)
    
    def checkIfCanBeFulfilled(self):
        """
        Checks if the order can be fulfilled.
        
        1/ All the blueprints involved by the jobs generated by this order are owned by the corp
        2/ ...
        
        If cannot be fulfilled, raise OrderCannotBeFulfilled exception which contains
        the list of missing blueprints.
        """
        missing_blueprints = set()
        for row in self.rows.all():
            try:
                bpo = Item.get(row.itemID).blueprint
                for bp in bpo.getInvolvedBlueprints(recurse=True):
                    if not OwnedBlueprint.objects.filter(blueprintTypeID=bp.blueprintTypeID).exists():
                        missing_blueprints.add(bp)
            except NoBlueprintException:
                pass
        if missing_blueprints:
            raise OrderCannotBeFulfilled(missing_blueprints=missing_blueprints)
            
            
            
    
    def createJobs(self):
        """
        Create all jobs needed to complete this order.
        """
        for row in self.rows.all():
            job = Job.create(row.itemID, row.quantity, order=self, row=row)
            job.createRequirements()


    def __unicode__(self):
        return 'Order #%d from %s' % (self.id, str(self.originator))

#------------------------------------------------------------------------------
class OrderLog(models.Model):
    
    order = models.ForeignKey(Order, related_name='logs')
    state = models.PositiveSmallIntegerField(choices=Order.STATES_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='logs')
    text = models.TextField()
    
#------------------------------------------------------------------------------
class OrderRow(models.Model):
    
    itemID = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, related_name='rows')
    __item = None
    
    def __getattribute__(self, attrname):
        if attrname == 'item':
            if self.__item is not None:
                return self.__item
            else:
                self.__item = Item.get(self.itemID) 
                return self.__item 
        else:
            return models.Model.__getattribute__(self, attrname)

    def getQuote(self):
        pass

    def __repr__(self):
        return '<OrderRow #%d: %d x%d>' % (self.id, self.itemID, self.quantity)

    def __unicode__(self):
        return '%s x%d' % (self.item.typeName, self.quantity)

#------------------------------------------------------------------------------
class Job(models.Model):

    PENDING = 0
    PLANNED = 1
    AGGREGATED = 2
    IN_PRODUCTION = 3
    READY = 4

    STATES_CHOICES = (
        (PENDING,       _('Pending')),
        (PLANNED,       _('Planned')),
        (AGGREGATED,    _('Aggregated')),
        (IN_PRODUCTION, _('In Production')),
        (READY,         _('Ready')),
    )

    SUPPLY = 0
    MANUFACTURING = 1
    INVENTION = 8
    
    ACTIVITY_CHOICES = (
        (MANUFACTURING, _('Manufacturing')),
        (SUPPLY,        _('Supply')),
        (INVENTION,     _('Invention')),
    )

    # self.order is None if this is an aggregation job
    order = models.ForeignKey(Order, related_name='jobs', null=True, blank=True)
    # self.row is not None only if this is a root job
    row = models.OneToOneField(OrderRow, related_name='job', null=True, blank=True)
    # self.parentJob is None if this job is directly issued from an OrderRow
    parentJob = models.ForeignKey('self', related_name='childrenJobs', null=True, blank=True)
    # 
    aggregators = models.ManyToManyField('self', related_name='aggregatedJobs')
    # when a job is aggregated by another one, it goes to the AGGREGATED state...
    state = models.PositiveSmallIntegerField(default=PENDING, choices=STATES_CHOICES) 
    
    factory = models.ForeignKey('FactorySlot', related_name='jobs', null=True, blank=True)

    owner = models.ForeignKey(User, related_name='jobs', null=True, blank=True)
    
    itemID = models.PositiveIntegerField()
    runs = models.PositiveIntegerField()
    blueprint = models.ForeignKey('OwnedBlueprint', related_name='jobs', null=True, blank=True)
    activity = models.SmallIntegerField(default=MANUFACTURING, choices=ACTIVITY_CHOICES)
    
    duration = models.BigIntegerField(default=0)
    
    maxDueDate = models.DateTimeField(null=True, blank=True)
    mileStone = models.ForeignKey(MileStone, related_name='jobs', null=True, blank=True)
    site = models.ForeignKey('ProductionSite', related_name='jobs')
    startDate = models.DateTimeField(null=True, blank=True) 
    endDate = models.DateTimeField(null=True, blank=True)

    __item = None

    def createRequirements(self):
        """
        Recursively create all jobs needed to complete the current one.
        
        SUPPLY jobs are trivial, they stop the recursion.
        """
        if self.activity == Job.SUPPLY:
            return # stop recursion
        
        materials = self.blueprint.getBillOfMaterials(runs=self.runs, 
                                                      meLevel=self.blueprint.me, 
                                                      activity=self.activity)
        
        for mat in materials:
            self.childrenJobs.add(Job.create(itemID=mat.requiredTypeID, 
                                             quantity=mat.quantity, 
                                             order=self.order))

        if self.blueprint.techLevel == 2:
            attempts  = InventionPolicy.attempts(self.blueprint)
            # add an INVENTION job
            self.childrenJobs.add(itemID=self.blueprint.blueprintTypeID, 
                                  runs=self.runs * attempts, 
                                  order=self.order,
                                  activity=Job.INVENTION)
        
        if self.activity == Job.INVENTION:
            # add a SUPPLY job for T1 BPCs
            self.childrenJobs.add(itemID=self.blueprint.parentBlueprintID, 
                                  runs=self.runs, 
                                  order=self.order,
                                  activity=Job.SUPPLY)
            decriptorTypeID  = InventionPolicy.decryptor(self.blueprint)
            if decriptorTypeID is not None:
                # add a SUPPLY job for a decryptor 
                self.childrenJobs.add(itemID=decriptorTypeID, 
                                      runs=self.runs, 
                                      order=self.order,
                                      activity=Job.SUPPLY)
            
        for job in self.childrenJobs.all():
            # recursive call
            job.createRequirements()
    
    @staticmethod
    def create(itemID, quantity, order, row=None):
        """
        Create a job (MANUFACTURING by default).
        
        If the item cannot be manufactured or if the corp does not own 
        the blueprint needed for the item, a SUPPLY job is created.
        
        The number of runs is calculated from the needed quantity 
        """        
        item = Item.get(row.itemID)
        try:
            bpID = item.blueprint.blueprintTypeID
            bp = OwnedBlueprint.objects.filter(blueprintTypeID=bpID).order_by('-me')[0]
            activity = Job.MANUFACTURING
            runs = quantity / item.portionSize
            if quantity % item.portionSize:
                runs += 1
            duration = item.blueprint.getDuration(runs=runs, peLevel=bp.pe)
        except IndexError:
            if item.techLevel == 2:
                # we're trying to manufacture a T2 item without owning its BPO
                # we must create an OwnedBlueprint for this job only (that will 
                # be consumed with it)
                # The invention policies are to be specified in InventionPolicies
                bp = InventionPolicy.blueprint(item.blueprint)
                runs = quantity / item.portionSize
                if quantity % item.portionSize:
                    runs += 1
                duration = item.blueprint.getDuration(runs=runs, peLevel=bp.pe)
                bp.runs = runs
                bp.save()
            else:
                bp = None
                activity = Job.SUPPLY
                duration = 0
                runs = quantity
        except NoBlueprintException:
            bp = None
            activity = Job.SUPPLY
            duration = 0
            runs = quantity
        
        return Job.objects.create(order=order, 
                                  row=row, 
                                  itemID=itemID, 
                                  blueprint=bp,
                                  runs=runs, 
                                  activity=activity, 
                                  duration=duration)

    def __getattribute__(self, attrname):
        if attrname == 'item':
            if self.__item is not None:
                return self.__item
            else:
                self.__item = Item.get(self.itemID) 
                return self.__item 
        else:
            return models.Model.__getattribute__(self, attrname)

#------------------------------------------------------------------------------
class ProductionSite(models.Model):
    
    locationID = models.BigIntegerField(primary_key=True)
    customName = models.CharField(max_length=255)
    discount = models.FloatField(default=0.0)



#------------------------------------------------------------------------------
class StockMargin(models.Model):
    
    site = models.ForeignKey(ProductionSite, related_name='stock_margins')
    typeID = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

#------------------------------------------------------------------------------
class StockLevel(models.Model):
    
    site = models.ForeignKey(ProductionSite, related_name='stock_levels')
    mileStone = models.ForeignKey(MileStone, related_name='stock_levels', null=True, blank=True)
    typeID = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    


#------------------------------------------------------------------------------
class FactorySlot(models.Model):
    
    site = models.ForeignKey(ProductionSite, related_name='slots')
    activity = models.SmallIntegerField(default=Job.MANUFACTURING, choices=Job.ACTIVITY_CHOICES)

#------------------------------------------------------------------------------
class OwnedBlueprint(models.Model):
    
    blueprintTypeID = models.PositiveIntegerField()
    me = models.PositiveIntegerField(default=0)
    pe = models.PositiveIntegerField(default=0)
    copy = models.BooleanField(default=False)
    runs = models.PositiveIntegerField(default=1)
    __blueprint = None
    
    def __getattr__(self, attrName):
        try:
            if self.__blueprint is not None:
                return Blueprint.__getattr__(self.__blueprint, attrName)
            else:
                self.__blueprint = Blueprint(*db.getBlueprint(self.blueprintTypeID))
                return Blueprint.__getattr__(self.__blueprint, attrName)
        except:
            return models.Model.__getattribute__(self, attrName)

    def __unicode__(self):
        return unicode(Blueprint.get(self.blueprintTypeID).typeName)


#------------------------------------------------------------------------------
class InventionPolicy(models.Model):
    
    itemGroupID = models.IntegerField(primary_key=True)
    itemGroupName = models.CharField(max_length=255)
    inventionChance = models.FloatField()
    targetME = models.IntegerField()

    @staticmethod
    def attempts(blueprint):
        _, _, _, _, _, attempts = InventionPolicy.resolve(blueprint)
        return attempts
    
    @staticmethod
    def blueprint(blueprint):
        _, runsPerBp, me, pe, _, _ = InventionPolicy.resolve(blueprint)
        return OwnedBlueprint(blueprintTypeID=blueprint.blueprintTypeID,
                              runs=runsPerBp,
                              original=False,
                              me=me,
                              pe=pe)

    @staticmethod
    def decryptor(blueprint):
        _, _, _, _, decriptorTypeID, _ = InventionPolicy.resolve(blueprint)
        return decriptorTypeID


    @staticmethod
    def resolve(blueprint):
        """
        Resolve which decryptor and how many invention runs must be used 
        to invent the given item group according to INVENTION_DEFAULT_POLICIES.
        
        If no decryptor is required, return None as the decryptor typeID 
        """
        decryptorGroup = constants.INTERFACES_DECRYPTOR_MAPPING[blueprint.parentBlueprint.dataInterfaceID]
        
        try:
            policy = InventionPolicy.objects.get(itemGroupID=blueprint.item.groupID)
        except InventionPolicy.DoesNotExist:
            policy = InventionPolicy.objects.get(itemGroupID=0)
        
        decriptorTypeID = None
        chance = policy.inventionChance
        runsPerBp = 1
        me = -4
        pe = -4
        for typeID, chanceMod, meMod, peMod, runsMod, _ in constants.DECRYPTORS[decryptorGroup]:
            if policy.targetME == (me + meMod):
                decriptorTypeID = typeID
                chance *= chanceMod
                me += meMod
                pe += peMod
                runsPerBp += runsMod
                break
        attempts = int(round(1.0 / chance))
        
        return blueprint.blueprintTypeID, runsPerBp, me, pe, decriptorTypeID, attempts

#------------------------------------------------------------------------------
class SupplyPrice(models.Model):
    
    typeID = models.PositiveIntegerField(primary_key=True)
    price = models.FloatField()
    
    def save(self, force_insert=False, force_update=False, using=None):
        models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using)
        # TODO create a price history reflecting the change
        pass

#------------------------------------------------------------------------------
class PriceHistory(models.Model):
    
    typeID = models.PositiveIntegerField()
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    

#------------------------------------------------------------------------------ 

class OrderCannotBeFulfilled(UserWarning):

    def __init__(self, missing_blueprints):
        self.missing_blueprints = missing_blueprints

    def __str__(self):
        output = "Missing Blueprints:\n\n"
        for bp in self.missing_blueprints:
            output += "  - %s\n" % bp.typeName
        return output

class IllegalStateError(UserWarning):
    pass