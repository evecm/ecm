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

from __future__ import with_statement

__date__ = "2011 8 17"
__author__ = "diabeteman"

from datetime import datetime

from django.db import models, transaction, connection
from django.contrib.auth.models import User

from ecm.core import utils
from ecm.core.utils import fix_mysql_quotes, cached_property
from ecm.core.eve.classes import NoBlueprintException
from ecm.plugins.industry.models.catalog import CatalogEntry
from ecm.plugins.industry.models.inventory import SupplyPrice
from ecm.plugins.industry.models.job import Job

#------------------------------------------------------------------------------
class Order(models.Model):
    """
    An order submitted by a User or the application.
    each order must follow the same life cycle specified by the VALID_TRANSITIONS hash table.
    An order can contain multiple rows (one for each different item)
    """

    class Meta:
        ordering = ['id']
        get_latest_by = 'id'
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


    state = models.PositiveIntegerField(default=DRAFT, choices=STATES.items())
    originator = models.ForeignKey(User, related_name='orders_created')
    manufacturer = models.ForeignKey(User, null=True, blank=True, related_name='orders_manufactured')
    deliveryMan = models.ForeignKey(User, null=True, blank=True, related_name='orders_delivered')
    client = models.CharField(max_length=255, null=True, blank=True)
    deliveryLocation = models.CharField(max_length=255, null=True, blank=True)
    deliveryDate = models.DateField(null=True, blank=True)
    quote = models.FloatField(default=0.0)
    pricing = models.ForeignKey('Pricing', related_name='orders')
    extraDiscount = models.FloatField(default=0.0)


    @property
    def lastModified(self):
        try:
            return self.logs.latest().date
        except:
            return datetime.now()

    @property
    def creationDate(self):
        try:
            return self.logs.all()[0].date
        except:
            return datetime.now()


    #############################
    # TRANSISTIONS

    def addComment(self, user, comment):
        self.logs.create(state=self.state, user=user, text=unicode(comment))

    def applyTransition(self, function, newState, user, comment):
        """
        Modify the state of an order. Adding a comment in the order logs.

        Checks if the new state is allowed in the life cycle. If not, raises an IllegalStateError
        """
        validTransitionNames = [ t.__name__ for t in Order.VALID_TRANSITIONS[self.state] ]
        if function.__name__ not in validTransitionNames:
            raise IllegalTransition('Cannot apply transition "%s" from state "%s".' %
                                    (function.__name__, Order.STATES[self.state]))
        else:
            self.state = newState
            self.addComment(user, comment)

    def modify(self, entries):
        """
        Modification of the order.
        An order can only be modified if its state is DRAFT or PENDING.

        entries must be a list of tuples such as :
        [(CatalogEntry_A, qty_A), (CatalogEntry_B, qty_B), (CatalogEntry_C, qty_C)]
        """
        if self.rows.all() or self.logs.all():
            comment = "Modified by originator."
        else:
            comment = "Created."
        self.applyTransition(Order.modify, Order.DRAFT, self.originator, comment)
        self.rows.all().delete()
        for catalogEntry, quantity in entries:
            self.rows.create(catalogEntry=catalogEntry, quantity=quantity)
        self.createJobs(dry_run=True)
        self.save()
    modify.text = 'Modify order'
    modify.id = 'modify'
    modify.customerAccess = True

    def confirm(self):
        """
        Originator's confirmation of the order. Warns the manufacturing team.
        """
        self.applyTransition(Order.confirm, Order.PENDING, self.originator, "Confirmed by originator.")
        self.save()
        # TODO: handle the alerts
    confirm.text = 'Confirm order'
    confirm.id = 'confirm'
    confirm.customerAccess = True

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
            self.applyTransition(Order.accept, Order.ACCEPTED, user=manufacturer, comment="Accepted")
            self.save()
            return True
        except OrderCannotBeFulfilled, err:
            self.applyTransition(Order.accept, Order.PROBLEMATIC, user=manufacturer, comment=str(err))
            self.save()
            return False
    accept.text = 'Accept order'
    accept.id = 'accept'
    accept.customerAccess = False

    def resolve(self, manufacturer, comment):
        """
        Resolution of a problematic order.

        This is a manual operation and entering a comment is mandatory to explain
        why the order was accepted despite the fact that is was PROBLEMATIC
        """
        self.createJobs()
        self.applyTransition(Order.resolve, Order.ACCEPTED, manufacturer, comment)
        self.save()
    resolve.text = 'Resolve order'
    resolve.id = 'resolve'
    resolve.customerAccess = False

    def plan(self, manufacturer, date):
        """
        Plan an order for a delivery date
        """
        self.applyTransition(Order.plan, Order.PLANNED, manufacturer,
                             'Order planned for date "%s"' % utils.print_date(date))
        self.deliveryDate = date
        self.save()
    plan.text = 'Plan order'
    plan.id = 'plan'
    plan.customerAccess = False

    def reject(self, manufacturer, comment):
        """
        Rejection of an order by a manufacturer.

        This is a manual operation and entering a comment is mandatory to explain
        why the order was rejected.
        """
        self.applyTransition(Order.reject, Order.REJECTED, manufacturer, comment)
        self.save()
        # TODO: handle the alerts
    reject.text = 'Reject order'
    reject.id = 'reject'
    reject.customerAccess = False

    def cancel(self, comment):
        """
        Cancellation of the order by its originator.
        """
        self.applyTransition(Order.cancel, Order.CANCELED, self.originator, comment)
        self.save()
    cancel.text = 'Cancel order'
    cancel.id = 'cancel'
    cancel.customerAccess = True

    def startPreparation(self, user=None):
        """
        Order preparation started (first job is started)
        """
        self.applyTransition(Order.startPreparation, Order.IN_PREPARATION,
                             user or self.manufacturer, "Preparation started.")
        self.save()
    startPreparation.text = 'Start preparation'
    startPreparation.id = 'startpreparation'
    startPreparation.customerAccess = False

    def endPreparation(self, manufacturer=None, deliveryMan=None):
        """
        Order is ready (all jobs are ready)

        Delivery task is assigned to manufacturer by default, unless deliveryMan is not None.
        """
        self.applyTransition(Order.endPreparation, Order.READY,
                             manufacturer, "Order is ready.")
        self.deliveryMan = deliveryMan or manufacturer or self.manufacturer

        self.save()
    endPreparation.text = 'End preparation'
    endPreparation.id = 'endpreparation'
    endPreparation.customerAccess = False

    def deliver(self, user=None):
        """
        Order has been delivered.
        """
        self.applyTransition(Order.deliver, Order.DELIVERED,
                             user or self.deliveryMan,
                             "Order has been delivered to the client.")
        self.save()
        # TODO: handle the alerts
    deliver.text = 'Deliver order'
    deliver.id = 'deliver'
    deliver.customerAccess = False

    def pay(self, user=None):
        """
        Order has been paid.
        """
        self.applyTransition(Order.pay, Order.PAID,
                             user or self.deliveryMan, "Order has been delivered to the client.")
        self.save()
    pay.text = 'Pay order'
    pay.id = 'pay'
    pay.customerAccess = True

    # allowed transitions between states
    VALID_TRANSITIONS = {
        DRAFT : (modify, confirm, cancel),
        PENDING : (modify, accept, cancel, reject),
        PROBLEMATIC : (modify, resolve, cancel, reject),
        ACCEPTED : (plan, startPreparation, cancel),
        PLANNED : (startPreparation, cancel),
        IN_PREPARATION : (endPreparation, cancel),
        READY : (deliver, cancel),
        DELIVERED : (pay, cancel),
        PAID : (),
        CANCELED : (),
        REJECTED : (),
    }

    @property
    def validTransitions(self):
        return self.getValidTransitions()

    @property
    def customerTransitions(self):
        return self.getValidTransitions(customer=True)


    def getValidTransitions(self, customer=False):
        if customer:
            return [ tr for tr in Order.VALID_TRANSITIONS[self.state] if tr.customerAccess ]
        else:
            return Order.VALID_TRANSITIONS[self.state]

    ################################
    # UTILITY FUNCTIONS

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
                if not row.catalogEntry.blueprints.all():
                    missing_blueprints.add(row.catalogEntry.blueprint)
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
        self.quote = 0.0
        for row in self.rows.all():
            row.cost, missPrices = row.calculateJobs(prices=prices, dry_run=dry_run)
            missingPrices.update(missPrices)
            self.quote += row.quote
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
            where.append('"activity" = %d')
        sql = 'SELECT "itemID", SUM("runs"), "activity" FROM "industry_job"'
        sql += ' WHERE ' + ' AND '.join(where)
        sql += ' GROUP BY "itemID", "activity" ORDER BY "activity", "itemID";'
        sql = fix_mysql_quotes(sql)

        cursor = connection.cursor() #@UndefinedVariable
        if activity is not None:
            cursor.execute(sql, [self.id, activity])
        else:
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
            for j in r.jobs.filter(parentJob=None):
                output += j.repr_as_tree()
        return output

    @property
    def url(self):
        return '/industry/orders/%d/' % self.id

    @property
    def permalink(self):
        return '<a href="%s" class="order">Order &#35;%d</a>' % (self.url, self.id)

    @property
    def stateText(self):
        return Order.STATES[self.state]

    def __unicode__(self):
        return 'Order #%d from %s [%s]' % (self.id, str(self.originator), Order.STATES[self.state])

    def __repr__(self):
        return unicode(self) + '\n  ' + '\n  '.join(map(unicode, list(self.rows.all())))




#------------------------------------------------------------------------------
class OrderLog(models.Model):

    class Meta:
        app_label = 'industry'
        get_latest_by = 'id'
        ordering = ['order', 'date']

    order = models.ForeignKey(Order, related_name='logs')
    state = models.PositiveSmallIntegerField(choices=Order.STATES.items())
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='logs')
    text = models.TextField()

    @cached_property
    def user_permalink(self):
        try:
            url = '/player/%d' % self.user.id
            return '<a href="%s" class="player">%s</a>' % (url, self.user.username)
        except:
            return '(None)'

    @property
    def state_text(self):
        try:
            return Order.STATES[self.state]
        except KeyError:
            return str(self.state)

    def __unicode__(self):
        return u'%s: [%s] (%s) %s' % (self.date, self.state_text, self.user, self.text)


#------------------------------------------------------------------------------
class OrderRow(models.Model):

    class Meta:
        app_label = 'industry'
        ordering = ['order']

    order = models.ForeignKey(Order, related_name='rows')
    catalogEntry = models.ForeignKey(CatalogEntry, related_name='order_rows')
    quantity = models.PositiveIntegerField()
    cost = models.FloatField(default=0.0)


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

        cursor = connection.cursor() #@UndefinedVariable
        cursor.execute(sql, [self.id])

        jobs = []
        for i, r, a in cursor:
            jobs.append(Job(itemID=i, runs=r, activity=a))
        cursor.close()

        return jobs


    @transaction.commit_manually
    def calculateJobs(self, prices=None, dry_run=False):
        job = Job.create(self.catalogEntry_id, self.quantity, order=self.order, row=self)
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

    @property
    def quote(self):
        if self.catalogEntry.fixedPrice is not None:
            return self.catalogEntry.fixedPrice
        else:
            return self.cost * (1 + self.order.pricing.margin)

    def __unicode__(self):
        return '%s x%d : %f' % (self.catalogEntry.typeName, self.quantity, self.cost)



#------------------------------------------------------------------------------
class OrderCannotBeFulfilled(UserWarning):

    def __init__(self, missing_blueprints):
        self.missing_blueprints = missing_blueprints

    def __str__(self):
        output = "Missing Blueprints:"  + "\n\n"
        for bp in self.missing_blueprints:
            output += "  - %s (%s)\n" % (str(bp.typeName), str(bp.typeID))
        return output

#------------------------------------------------------------------------------
class IllegalTransition(UserWarning): pass

