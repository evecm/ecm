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

__date__ = "2011 8 17"
__author__ = "diabeteman"

from django.db import models, transaction, connection
from django.contrib.auth.models import User

from ecm.core.utils import fix_mysql_quotes
from ecm.core.eve.classes import Item, NoBlueprintException

from ecm.data.industry.models.catalog import OwnedBlueprint, CatalogEntry
from ecm.data.industry.models.inventory import SupplyPrice
from ecm.data.industry.models.job import Job

#------------------------------------------------------------------------------
class Order(models.Model):
    """
    An order submitted by a User or the application.
    each order must follow the same life cycle specified by the VALID_TRANSITIONS hash table.
    An order can contain multiple rows (one for each different item)
    """

    class Meta:
        ordering = ['id']
        app_label = 'industry'

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
    STATES = {
        DRAFT:             'Draft',
        PENDING:           'Pending',
        PROBLEMATIC:       'Problematic',
        ACCEPTED:          'Accepted',
        PLANNED:           'Planned',
        IN_PREPARATION:    'In Preparation',
        READY:             'Ready',
        DELIVERED:         'Delivered',
        PAID:              'Paid',
        CANCELED:          'Canceled by Client',
        REJECTED:          'Rejected by Manufacturer',
    }
    
    # allowed transitions between states
    VALID_TRANSITIONS = {
        DRAFT : (DRAFT, PENDING, CANCELED),
        PENDING : (DRAFT, PROBLEMATIC, ACCEPTED, CANCELED, REJECTED),
        PROBLEMATIC : (DRAFT, ACCEPTED, REJECTED, CANCELED),
        ACCEPTED : (PLANNED, IN_PREPARATION, CANCELED),
        PLANNED : (IN_PREPARATION, CANCELED),
        IN_PREPARATION : (READY, CANCELED),
        READY : (DELIVERED, CANCELED),
        DELIVERED : (PAID, CANCELED),
        PAID : (),
        CANCELED : (),
        REJECTED : (),
    }
    
    state = models.PositiveIntegerField(default=DRAFT, choices=STATES.items())
    originator = models.ForeignKey(User, related_name='orders_created')
    manufacturer = models.ForeignKey(User, null=True, blank=True, related_name='orders_manufactured')
    deliveryMan = models.ForeignKey(User, null=True, blank=True, related_name='orders_delivered')
    client = models.CharField(max_length=255, null=True, blank=True)
    deliveryLocation = models.CharField(max_length=255, null=True, blank=True)
    mileStone = models.ForeignKey('MileStone', related_name='orders', null=True, blank=True)
    quote = models.FloatField(default=0.0)
    pricing = models.ForeignKey('Pricing', related_name='orders')
    extraDiscount = models.FloatField(default=0.0)
    
    #############################
    # TRANSISTIONS
    
    def addComment(self, user, comment):
        self.logs.create(state=self.state, user=user, text=str(comment))
    
    def changeState(self, newState, user, comment):
        """
        Modify the state of an order. Adding a comment in the order logs.
        
        Checks if the new state is allowed in the life cycle. If not, raises an IllegalStateError
        """
        if newState not in Order.VALID_TRANSITIONS[self.state]:
            raise IllegalStateError('Cannot change state from "%s" to "%s".' % 
                                    (Order.STATES[self.state], Order.STATES[newState]))
        else:
            self.state = newState
            self.addComment(user, comment)
    
    @transaction.commit_on_success
    def modify(self, newItems):
        """
        Modification of the order. 
        An order can only be modified if its state is DRAFT or PENDING.
        
        newItems must be a list of tuples such as :
        [(itemID_A, qty_A), (itemID_B, qty_B), (itemID_C, qty_C)]
        """
        if self.rows.all() or self.logs.all():
            comment = "Modified by originator."
        else:
            comment = "Created."
        self.changeState(Order.DRAFT, self.originator, comment)
        self.rows.all().delete()
        for itemID, quantity in newItems:
            self.rows.create(itemID=itemID, quantity=quantity)
        self.createJobs(dry_run=True)
        self.save()
    
    @transaction.commit_on_success
    def confirm(self):
        """
        Originator's confirmation of the order. Warns the manufacturing team. 
        """
        self.changeState(Order.PENDING, self.originator, "Confirmed by originator.")
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
            self.changeState(Order.ACCEPTED, user=manufacturer, comment="Accepted")
            self.save()
            return True
        except OrderCannotBeFulfilled as err:
            self.changeState(Order.PROBLEMATIC, user=manufacturer, comment=str(err))
            self.save()
            return False 
    
    def resolve(self, manufacturer, comment):
        """
        Resolution of a problematic order.
        
        This is a manual operation and entering a comment is mandatory to explain 
        why the order was accepted despite the fact that is was PROBLEMATIC
        """
        self.createJobs()
        self.changeState(Order.ACCEPTED, manufacturer, comment)
        self.save()
    
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
                blueprint = Item.new(row.itemID).blueprint
                for bp in blueprint.getInvolvedBlueprints(recurse=True):
                    if not OwnedBlueprint.objects.filter(blueprintTypeID=bp.typeID).exists():
                        missing_blueprints.add(bp)
            except NoBlueprintException:
                pass
        if missing_blueprints:
            raise OrderCannotBeFulfilled(missing_blueprints=missing_blueprints)
    
    def createJobs(self, dry_run=False):
        """
        Create all jobs needed to complete this order.
        Calculating costs for all the order's rows.
        
        If dry_run is True, only the prices are written, and any job creation is rollbacked.
        """
        prices = {}
        for sp in SupplyPrice.objects.all():
            prices[sp.typeID] = sp.price
        missingPrices = set([])
        for row in self.rows.all():
            row.cost, missPrices = row.calculateJobs(prices=prices, dry_run=dry_run)
            missingPrices.add(missPrices)
            if row.catalogEntry.fixedPrice is not None:
                self.quote += row.catalogEntry.fixedPrice
            else:
                self.quote += row.cost * (1 + self.pricing.margin)
            row.save()
        self.save()
        with transaction.commit_on_success():
            for itemID in missingPrices:
                SupplyPrice.objects.create(typeID=itemID, price=0.0)


    def getAggregatedJobs(self, activity=None):
        """
        Retrieve a list of all the jobs related to this order aggregated by itemID.
        
        The job activity can be filtered to display only SUPPLY jobs
        """
        where = [ '"order_id" = %s' ]
        if activity is not None:
            where.append('"activity" = %d' % activity)
        sql = 'SELECT "itemID", SUM("runs"), "activity" FROM "industry_job"'
        sql += ' WHERE ' + ' AND '.join(where)
        sql += ' GROUP BY "itemID", "activity" ORDER BY "activity", "itemID";'
        sql = fix_mysql_quotes(sql)
        
        cursor = connection.cursor()
        cursor.execute(sql, [self.id])
        
        jobs = []
        for i, r, a in cursor:
            jobs.append(Job(itemID=i, runs=r, activity=a))
        cursor.close()
        
        return jobs
    
    def __getattr__(self, attr):
        if attr.endswith('_permalink'):
            field = attr[:-len('_permalink')]
            if field in ('originator', 'manufacturer', 'deliveryMan'):
                player_id = getattr(self, field + '_id')
                if player_id is not None:
                    url = '/player/%d' % player_id
                    return '<a href="%s" class="player">%s</a>' % (url, getattr(self, field).username)
                else:
                    return '(none)'
            else:
                return models.Model.__getattribute__(self, attr)
        else:
            return models.Model.__getattribute__(self, attr)
    
    def repr_as_tree(self):
        output = ''
        for r in self.rows.all():
            for j in r.job.filter(parentJob=None):
                output += j.repr_as_tree()
        return output

    def __unicode__(self):
        return 'Order #%d from %s [%s]' % (self.id, str(self.originator), Order.STATES[self.state])

    def __repr__(self):
        return unicode(self) + '\n  ' + '\n  '.join(map(unicode, list(self.rows.all())))

#------------------------------------------------------------------------------
class OrderLog(models.Model):
    
    class Meta:
        app_label = 'industry'
        ordering = ['order', 'date']
    
    order = models.ForeignKey(Order, related_name='logs')
    state = models.PositiveSmallIntegerField(choices=Order.STATES.items())
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='logs')
    text = models.TextField()
    
    def __unicode__(self):
        return u'%s: [%s] (%s) %s' % (self.date, Order.STATES.get(self.state), self.user, self.text)
    
    
#------------------------------------------------------------------------------
class OrderRow(models.Model):
    
    class Meta:
        app_label = 'industry'
        ordering = ['order']
    
    order = models.ForeignKey(Order, related_name='rows')
    catalogEntry = models.ForeignKey(CatalogEntry, related_name='order_rows')
    quantity = models.PositiveIntegerField()
    cost = models.FloatField(default=0.0)
    __item = None
    
    
    def getAggregatedJobs(self, activity=None):
        """
        Retrieve a list of all the jobs related to this OrderRow aggregated by itemID.
        
        The job activity can be filtered to display only SUPPLY jobs
        """
        where = [ '"row_id" = %s' ]
        if activity is not None:
            where.append('"activity" = %d' % activity)
        sql = 'SELECT "itemID", SUM("runs"), "activity" FROM "industry_job"'
        sql += ' WHERE ' + ' AND '.join(where)
        sql += ' GROUP BY "itemID", "activity" ORDER BY "activity", "itemID";'
        sql = fix_mysql_quotes(sql)
        
        cursor = connection.cursor()
        cursor.execute(sql, [self.id])
        
        jobs = []
        for i, r, a in cursor:
            jobs.append(Job(itemID=i, runs=r, activity=a))
        cursor.close()
        
        return jobs
    
    @transaction.commit_manually
    def calculateJobs(self, prices=None, dry_run=False):
        job = Job.create(self.itemID, self.quantity, order=self.order, row=self)
        job.createRequirements()
        cost, missingPrices = self.calculateCost(prices)
        if dry_run:
            transaction.rollback()
        else:
            transaction.commit()
        return cost, missingPrices

    def calculateCost(self, prices=None):
        if prices is None:
            prices = {}
            for sp in SupplyPrice.objects.all():
                prices[sp.typeID] = sp.price
        cost = 0.0
        missingPrices = set([])
        for job in self.getAggregatedJobs(Job.SUPPLY):
            try:
                cost += prices[job.itemID] * round(job.runs)
            except KeyError:
                # to avoid the error next time :)
                missingPrices.add(job.itemID)
        return cost, missingPrices

    def __unicode__(self):
        return '%s x%d : %f' % (self.catalogEntry.typeName, self.quantity, self.cost)



#------------------------------------------------------------------------------ 
class OrderCannotBeFulfilled(UserWarning):

    def __init__(self, missing_blueprints):
        self.missing_blueprints = missing_blueprints

    def __str__(self):
        output = "Missing Blueprints:\n\n"
        for bp in self.missing_blueprints:
            output += "  - %s (%s)\n" % (str(bp.typeName), str(bp.typeID))
        return output

#------------------------------------------------------------------------------
class IllegalStateError(UserWarning): pass

