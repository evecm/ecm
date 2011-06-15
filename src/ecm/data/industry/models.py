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
from ecm.core.eve.classes import Item, Blueprint
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


#------------------------------------------------------------------------------
class DeliveryDate(models.Model):
    date = models.DateField()
    
    def next(self):
        next_date = self.date + timedelta(days=settings.DELIVERY_INTERVAL_DAYS)
        return self.objects.get_or_create(date=next_date)
    
    def prev(self):
        prev_date = self.date - timedelta(days=settings.DELIVERY_INTERVAL_DAYS)
        return self.objects.get_or_create(date=prev_date)

#------------------------------------------------------------------------------
class Order(models.Model):
    
    PENDING = 0
    ACCEPTED = 1
    PLANNED = 2
    IN_PREPARATION = 3
    READY = 4
    DELIVERED = 5
    PAID = 6
    CANCELED_BY_CLIENT = 7
    REJECTED_BY_MANUFACTURER = 8
    
    STATES_CHOICES = (
        (PENDING,                   _('Pending')),
        (ACCEPTED,                  _('Accepted')),
        (PLANNED,                   _('Planned')),
        (IN_PREPARATION,            _('In Preparation')),
        (READY,                     _('Ready')),
        (DELIVERED,                 _('Delivered')),
        (PAID,                      _('Paid')),
        (CANCELED_BY_CLIENT,        _('Canceled by Client')),
        (REJECTED_BY_MANUFACTURER,  _('Rejected by Manufacturer')),
    )
    
    VALID_TRANSITIONS = {
        PENDING : (ACCEPTED, PLANNED, CANCELED_BY_CLIENT, REJECTED_BY_MANUFACTURER),
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
    deliveryDate = models.ForeignKey(DeliveryDate, related_name='orders', null=True, blank=True)
    state = models.PositiveIntegerField(default=PENDING, choices=STATES_CHOICES)
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

    def updateJobs(self):
        for row in self.rows.all():
            if row.job is None:
                # no job associated to row yet
                try:
                    bp = OwnedBlueprint.objects.filter(productTypeID=row.itemID).order_by('me')[0]
                except IndexError:
                    bp = None
                row.job = Job.objects.create(order=self, row=row, itemID=row.itemID, 
                                             quantity=row.quantity, blueprint=bp,
                                             activity=Job.MANUFACTURING)
                row.job.createRequirements()



    def __unicode__(self):
        return 'Order #%d from %s' % (self.id, self.originator)

#------------------------------------------------------------------------------
class OrderComment(models.Model):
    
    order = models.ForeignKey(Order, related_name='comments')
    state = models.PositiveSmallIntegerField(choices=Order.STATES_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='comments')
    text = models.TextField()
    
#------------------------------------------------------------------------------
class OrderRow(models.Model):
    
    itemID = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(Order, related_name='rows')
    
    def __getattribute__(self, attrname):
        if attrname == 'item':
            try:
                return self.__item
            except AttributeError:
                self.__item = Item.get(self.itemID) 
                return self.__item 
        else:
            return models.Model.__getattribute__(self, attrname)

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
    quantity = models.PositiveIntegerField()
    blueprint = models.ForeignKey('OwnedBlueprint', related_name='jobs', null=True, blank=True)
    activity = models.SmallIntegerField(default=MANUFACTURING, choices=ACTIVITY_CHOICES)
    
    duration = models.BigIntegerField()
    
    maxDueDate = models.DateTimeField(null=True, blank=True)
    deliveryDate = models.ForeignKey(DeliveryDate, related_name='jobs', null=True, blank=True)
    startDate = models.DateTimeField(null=True, blank=True) 
    endDate = models.DateTimeField(null=True, blank=True)


    def createRequirements(self):
        if self.blueprint is not None:
            activity = self.blueprint.activities[self.activity]
            for req in activity.requirements:
                pass
        # else: stop recursion
            

    def __getattribute__(self, attrname):
        if attrname == 'item':
            try:
                return self.__item
            except AttributeError:
                self.__item = Item.get(self.itemID) 
                return self.__item 
        else:
            return models.Model.__getattribute__(self, attrname)

#------------------------------------------------------------------------------
class ProductionSite(models.Model):
    
    locationID = models.PositiveIntegerField(primary_key=True)
    customName = models.CharField(max_length=256)
    discount = models.FloatField(default=0.0)

#------------------------------------------------------------------------------
class FactorySlot(models.Model):
    
    site = models.ForeignKey(ProductionSite, related_name='slots')
    activity = models.SmallIntegerField(default=Job.MANUFACTURING, choices=Job.ACTIVITY_CHOICES)

#------------------------------------------------------------------------------
class OwnedBlueprint(models.Model):
    
    blueprintID = models.PositiveIntegerField()
    count = models.PositiveIntegerField(default=1)
    original = models.BooleanField(default=True)
    me = models.PositiveIntegerField(default=0)
    pe = models.PositiveIntegerField(default=0)
    
    def __getattr__(self, attrname):
        if attrname == '__blueprint':
            raise AttributeError()
        try:
            try:
                getattr(self, '__blueprint')
            except AttributeError:
                self.__blueprint = Blueprint.get(self.blueprintID)
            return getattr(self.__blueprint, attrname)
        except AttributeError:
            return models.Model.__getattribute__(self, attrname)
    
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------ 
class IllegalStateError(UserWarning):
    pass
