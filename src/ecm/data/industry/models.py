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

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

#------------------------------------------------------------------------------
class Order(models.Model):
    
    SUBMITTED = 0
    ACCEPTED = 1
    PLANNED = 2
    IN_PREPARATION = 3
    READY = 4
    DELIVERED = 5
    PAID = 6
    CANCELED_BY_CLIENT = 7
    REJECTED_BY_MANUFACTURER = 8
    
    STATES = {
        SUBMITTED : _('Submitted'),
        ACCEPTED : _('Accepted'),
        PLANNED : _('Planned'),
        IN_PREPARATION : _('In Preparation'),
        READY : _('Ready'),
        DELIVERED : _('Delivered'),
        PAID : _('Paid'),
        CANCELED_BY_CLIENT : _('Canceled by Client'),
        REJECTED_BY_MANUFACTURER : _('Rejected by Manufacturer'),
    }
    
    VALID_TRANSITIONS = {
        SUBMITTED : (ACCEPTED, PLANNED, CANCELED_BY_CLIENT, REJECTED_BY_MANUFACTURER),
        ACCEPTED : (IN_PREPARATION, CANCELED_BY_CLIENT),
        PLANNED : (IN_PREPARATION, CANCELED_BY_CLIENT),
        IN_PREPARATION : (READY, CANCELED_BY_CLIENT),
        READY : (DELIVERED, CANCELED_BY_CLIENT),
        DELIVERED : (PAID, CANCELED_BY_CLIENT),
        PAID : (),
        CANCELED_BY_CLIENT : (),
        REJECTED_BY_MANUFACTURER : (),
    }
    
    originator = models.ForeignKey(User, related_name='orders_created')
    manufacturer = models.ForeignKey(User, null=True, blank=True, related_name='orders_manufactured')
    deliveryMan = models.ForeignKey(User, null=True, blank=True, related_name='orders_delivered')
    client = models.CharField(max_length=256, null=True, blank=True)
    deliveryLocation = models.CharField(max_length=256, null=True, blank=True)
    deliveryDate = models.DateField(null=True, blank=True)
    state = models.PositiveIntegerField(default=SUBMITTED)
    discount = models.FloatField(default=0.0)
    quote = models.FloatField(null=True, blank=True)
    
    #############################
    # TRANSISTIONS
    
    def changeState(self, newState, user, comment):
        assert isinstance(user, User)
        if newState not in Order.VALID_TRANSITIONS[newState]:
            legalStates = str([ Order.STATES[s] for s in Order.VALID_TRANSITIONS[newState] ])
            raise IllegalStateError(Order.STATES[newState]+' is illegal. Only '+legalStates+' are allowed.')
        self.state = newState
        self.comments.create(order=self, state=self.state, user=user, text=str(comment))
    
    def cancel(self, user, reason):
        self.changeState(Order.CANCELED_BY_CLIENT, user, reason)
        self.save()
        
    def rejectByManufacturer(self, user, reason):
        self.changeState(Order.REJECTED_BY_MANUFACTURER, user, reason)
        self.manufacturer = user
        self.save()
    
    def startPreparation(self, user, reason=""):
        self.changeState(Order.IN_PREPARATION, user, reason)
        self.manufacturer = user
        self.save()
    
    def endPreparation(self, user, reason=""):
        self.changeState(Order.READY, user, reason)
        self.save()
    
    def deliver(self, user, reason=""):
        self.changeState(Order.DELIVERED, user, reason)
        self.deliveryMan = user
        self.save()
        
    def pay(self, user, reason=""):
        self.changeState(Order.PAID, user, reason)
        self.save()
        
    def rejectByClient(self, user, reason):
        self.changeState(Order.REJECTED_BY_CLIENT, user, reason)
        self.save()

    def __unicode__(self):
        return 'Order #%d from %s' % (self.id, self.originator)

#------------------------------------------------------------------------------
class OrderComment(models.Model):
    
    order = models.ForeignKey(Order, related_name='comments')
    state = models.PositiveSmallIntegerField()
    date = models.DateTimeField()
    user = models.ForeignKey(User, related_name='comments')
    text = models.TextField()
    
#------------------------------------------------------------------------------
class OrderRow(models.Model):
    
    typeID = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, related_name='rows')



    
#------------------------------------------------------------------------------
class JobType(models.Model):
    
    name = models.CharField(max_length=256)
    needsPlanning = models.BooleanField(default=False)
    needsSpecialFactory = models.BooleanField(default=False)

#------------------------------------------------------------------------------
class ProductionSite(models.Model):
    
    locationID = models.PositiveIntegerField(primary_key=True)
    customName = models.CharField(max_length=256)
    natures = models.ManyToManyField(JobType, related_name='sites')
    discount = models.FloatField(default=0.0)
    

#------------------------------------------------------------------------------
class OwnedBlueprint(models.Model):
    
    typeID = models.PositiveIntegerField(primary_key=True)
    count = models.PositiveIntegerField()
    original = models.BooleanField(default=True)
    me = models.PositiveIntegerField()
    pe = models.PositiveIntegerField()
    
    
    
#------------------------------------------------------------------------------
class Job(models.Model):

    IDLE = 0
    PLANNED = 1
    AGGREGATED = 2
    STARTED = 3
    READY = 4

    STATES = {
        IDLE : _('Idle'),
        PLANNED : _('Planned'),
        AGGREGATED : _('Aggregated'),
        STARTED : _('In Production'),
        READY : _('Ready'),
    }
            

    order = models.ForeignKey(Order, related_name='jobs')
    blueprint = models.ForeignKey(OwnedBlueprint, related_name='jobs')
    factory = models.ForeignKey(FactorySlot, related_name='jobs')
    type = models.ForeignKey(JobType, related_name='jobs')
    aggregators = models.ManyToManyField('self', related_name='aggregatedJobs')
    parentJob = models.ForeighKey('self', related_name='childrenJobs')
    aggregateShare = models.FloatField(default=1.0)
    state = models.PositiveSmallIntegerField(IDLE) # when a job is aggregated by another one, it goes to standby mode...
    dueDate = models.DateTimeField()
    duration = models.BigIntegerField()


    
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self, *args, **kwargs)
        
        

#------------------------------------------------------------------------------
class JobIngredient(models.Model):
    
    job = models.ForeignKey(Job, related_name='ingredients')
    typeID = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------ 
class IllegalStateError(UserWarning):
    pass
