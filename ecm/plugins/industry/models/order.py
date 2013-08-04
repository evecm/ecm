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

from __future__ import with_statement

__date__ = "2011 8 17"
__author__ = "diabeteman"

from django.db import models, connection
from django.contrib.auth.models import User

from ecm.utils import db
from ecm.apps.eve.models import Type
from ecm.plugins.industry.models.catalog import CatalogEntry, PricingPolicy
from ecm.plugins.industry.models.inventory import Supply
from ecm.plugins.industry.models.job import Job
from ecm.plugins.industry.models.research import InventionError

#------------------------------------------------------------------------------
class Order(models.Model):
    """
    An order submitted by a User or the application.
    each order must follow the same life cycle specified by the VALID_TRANSITIONS hash table.
    An order can contain multiple rows (one for each different item)
    """

    class Meta:
        get_latest_by = 'id'
        app_label = 'industry'

    # states
    DRAFT = 0
    PENDING = 1
    PROBLEMATIC = 2
    ACCEPTED = 3
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
        IN_PREPARATION:    'In Preparation',
        READY:             'Ready',
        DELIVERED:         'Delivered',
        PAID:              'Paid',
        CANCELED:          'Canceled by Client',
        REJECTED:          'Rejected by Responsible',
    }

    state = models.PositiveIntegerField(default=DRAFT, choices=STATES.items())
    originator = models.ForeignKey(User, related_name='orders_created')
    responsible = models.ForeignKey(User, null=True, blank=True, related_name='orders_responsible')
    delivery_boy = models.ForeignKey(User, null=True, blank=True, related_name='orders_delivered')
    client = models.CharField(max_length=255, null=True, blank=True)
    delivery_location = models.CharField(max_length=255, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    quote = models.FloatField(default=0.0)

    def last_modified(self):
        try:
            return self.logs.latest().date
        except OrderLog.DoesNotExist:
            return None

    def creation_date(self):
        try:
            return self.logs.all()[0].date
        except IndexError:
            return None


    #############################
    # TRANSISTIONS

    def add_comment(self, user, comment):
        self.logs.create(state=self.state, user=user, text=unicode(comment))

    def apply_transition(self, function, state, user, comment):
        """
        Modify the state of an order. Adding a comment in the order logs.

        Checks if the new state is allowed in the life cycle. If not, raises an IllegalStateError
        """
        self.check_can_pass_transition(function.__name__)
        self.state = state
        self.add_comment(user, comment)

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
        self.apply_transition(Order.modify, Order.DRAFT, self.originator, comment)
        self.rows.all().delete()

        self.quote = 0.0
        missing_price = False
        for entry, quantity in entries:
            cost = 0.0
            surcharge = 0.0
            if entry.production_cost is None and entry.fixed_price is None:
                missing_price = True
            else:
                if entry.fixed_price is not None:
                    surcharge = entry.fixed_price
                else:
                    cost = entry.production_cost
                    surcharge = PricingPolicy.resolve_surcharge(entry, self.originator, cost)
            
            self.quote += quantity * (cost + surcharge)
            self.rows.create(catalog_entry=entry, 
                             quantity=quantity, 
                             cost=cost, 
                             surcharge=surcharge)
        if missing_price:
            self.quote = 0.0
        self.save()

    def confirm(self):
        """
        Originator's confirmation of the order. Warns the manufacturing team.
        """
        self.apply_transition(Order.confirm, Order.PENDING, self.originator, "Confirmed by originator.")
        self.save()
        # TODO: handle the alerts to the manufacturing team

    def accept(self, user):
        """
        Acceptation by a responsible.
        The order cannot be modified by its originator after acceptation.

        During the "accept" transition, we check if the order can be fulfilled.
        If it can, its states changes to ACCEPTED. If not, the order changes to PROBLEMATIC.
        """
        try:
            self.check_feasibility()
            missing_prices = self.create_jobs(calculate_surcharge=True)
            if missing_prices: # FIXME: moche moche moche
                raise OrderCannotBeFulfilled('Missing prices for items %s' % list(missing_prices))
            self.apply_transition(Order.accept, Order.ACCEPTED, user=user, comment="Accepted")
            self.responsible = user
            self.save()
            return True
        except OrderCannotBeFulfilled, err:
            self.apply_transition(Order.accept, Order.PROBLEMATIC, user=user, comment=unicode(err))
            self.responsible = user
            self.save()
            return False

    def resolve(self, user, comment):
        """
        Resolution of a problematic order.

        This is a manual operation and entering a comment is mandatory to explain
        why the order was accepted despite the fact that is was PROBLEMATIC
        """
        self.create_jobs(calculate_surcharge=True)
        self.apply_transition(Order.resolve, Order.ACCEPTED, user, comment)
        self.responsible = user
        self.save()

    def reject(self, user, comment):
        """
        Rejection of an order by a responsible.

        This is a manual operation and entering a comment is mandatory to explain
        why the order was rejected.
        """
        self.apply_transition(Order.reject, Order.REJECTED, user, comment)
        self.save()
        # TODO: handle the alerts to the client

    def cancel(self, comment):
        """
        Cancellation of the order by its originator.
        """
        self.apply_transition(Order.cancel, Order.CANCELED, self.originator, comment)
        self.save()
        # TODO: handle the alerts to the manufacturing team

    def start_preparation(self, user=None):
        """
        Order preparation started (first job is started)
        """
        self.apply_transition(Order.start_preparation, Order.IN_PREPARATION,
                              user or self.responsible, 'Preparation started.')
        self.save()

    def end_preparation(self, responsible=None, delivery_boy=None):
        """
        Order is ready (all jobs are ready)

        Delivery task is assigned to responsible by default, unless delivery_boy is not None.
        """
        self.apply_transition(Order.end_preparation, Order.READY,
                              responsible, 'Order is ready.')
        self.delivery_boy = delivery_boy or responsible or self.responsible
        self.jobs.all().update(state=Job.READY)
        self.save()

    def deliver(self, user=None):
        """
        Order has been delivered.
        """
        self.apply_transition(Order.deliver, Order.DELIVERED,
                              user or self.delivery_boy,
                              'Order has been delivered to the client.')
        self.save()
        # TODO: handle the alerts to the client

    def record_payment(self, user=None):
        """
        Order has been paid.
        """
        self.apply_transition(Order.record_payment, Order.PAID,
                              user or self.delivery_boy, 
                              'Payment received.')
        self.save()

    # allowed transitions between states
    VALID_TRANSITIONS = {
        DRAFT : (modify, confirm, cancel),
        PENDING : (modify, accept, cancel, reject),
        PROBLEMATIC : (modify, resolve, cancel, reject),
        ACCEPTED : (start_preparation, cancel),
        IN_PREPARATION : (end_preparation, cancel),
        READY : (deliver, cancel),
        DELIVERED : (record_payment, cancel),
        PAID : (),
        CANCELED : (),
        REJECTED : (),
    }

    modify.customer_access = True
    confirm.customer_access = True
    accept.customer_access = False
    resolve.customer_access = False
    reject.customer_access = False
    cancel.customer_access = True
    start_preparation.customer_access = False
    end_preparation.customer_access = False
    deliver.customer_access = False
    record_payment.customer_access = False


    def get_valid_transitions(self, customer=False):
        return [ tr for tr in Order.VALID_TRANSITIONS[self.state] if customer == tr.customer_access ]

    def check_can_pass_transition(self, function_name):
        valid_functions_names = [ t.__name__ for t in Order.VALID_TRANSITIONS[self.state] ]
        if function_name not in valid_functions_names:
            raise IllegalTransition('Cannot apply transition "%s" from state "%s".' % 
                                    (function_name, Order.STATES[self.state]))

    ################################
    # UTILITY FUNCTIONS

    def check_feasibility(self):
        """
        Checks if the order can be fulfilled.

        1/ All the blueprints involved by the jobs generated by this order are owned by the corp
        2/ ...

        If cannot be fulfilled, raise OrderCannotBeFulfilled exception which contains
        the list of missing blueprints.
        """
        missing_blueprints = set()
        for row in self.rows.all():
            missing_blueprints.update(row.catalog_entry.missing_blueprints())

        if missing_blueprints:
            raise OrderCannotBeFulfilled(missing_blueprints=missing_blueprints)

    def create_jobs(self, ignore_fixed_prices=False, calculate_surcharge=False):
        """
        Create all jobs needed to complete this order.
        Calculating costs for all the order's rows.
        """
        prices = {}
        for sp in Supply.objects.all():
            prices[sp.typeID] = sp.price
        all_missing_prices = set([])
        
        self.quote = 0.0
        
        for row in self.rows.all():
            cost, miss_prices = row.create_jobs(prices=prices)
            all_missing_prices.update(miss_prices)
            
            if ignore_fixed_prices or row.catalog_entry.fixed_price is None:
                if calculate_surcharge:
                    surcharge = PricingPolicy.resolve_surcharge(row.catalog_entry, self.originator, row.cost)
                else:
                    surcharge = 0.0
            else:
                surcharge = row.catalog_entry.fixed_price * row.quantity
                cost = 0.0
            
            row.surcharge = surcharge
            row.cost = cost
            row.save()
            self.quote += cost + surcharge
            
        self.save()
        
        return all_missing_prices

    def get_bill_of_materials(self):
        return self.get_aggregated_jobs(Job.SUPPLY)

    def get_aggregated_jobs(self, activity=None):
        """
        Retrieve a list of all the jobs related to this order aggregated by item_id.

        The job activity can be filtered to display only SUPPLY jobs
        """
        where = [ '"order_id" = %s' ]
        if activity is not None:
            where.append('"activity" = %s')
        sql = 'SELECT "item_id", SUM("runs"), "activity" FROM "industry_job"'
        sql += ' WHERE ' + ' AND '.join(where)
        sql += ' GROUP BY "item_id", "activity" ORDER BY "activity", "item_id";'
        sql = db.fix_mysql_quotes(sql)

        cursor = connection.cursor() #@UndefinedVariable
        if activity is not None:
            cursor.execute(sql, [self.id, activity])
        else:
            cursor.execute(sql, [self.id])

        jobs = []
        for i, r, a in cursor:
            jobs.append(Job(item_id=i, runs=r, activity=a))
        cursor.close()

        return jobs

    def repr_as_tree(self):
        output = ''
        for r in self.rows.all():
            for j in r.jobs.filter(parent_job=None):
                output += j.repr_as_tree()
        return output

    def url(self):
        return '/industry/orders/%d/' % self.id

    def shop_url(self):
        return '/shop/orders/%d/' % self.id

    def permalink(self, shop=True):
        if shop:
            url = self.shop_url()
        else:
            url = self.url()
        return '<a href="%s" class="order">Order &#35;%d</a>' % (url, self.id)

    def originator_permalink(self):
        if self.originator is not None:
            url = '/hr/players/%d/' % self.originator.id
            return '<a href="%s" class="player">%s</a>' % (url, self.originator.username)
        else:
            return '(none)'

    def responsible_permalink(self):
        if self.responsible is not None:
            url = '/hr/players/%d/' % self.responsible.id
            return '<a href="%s" class="player">%s</a>' % (url, self.responsible.username)
        else:
            return '(none)'

    def delivery_boy_permalink(self):
        if self.delivery_boy is not None:
            url = '/hr/players/%d/' % self.delivery_boy.id
            return '<a href="%s" class="player">%s</a>' % (url, self.delivery_boy.username)
        else:
            return '(none)'

    def state_text(self):
        return Order.STATES[self.state]

    def __unicode__(self):
        return unicode(self.id)


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

    def user_permalink(self):
        try:
            url = '/players/%d/' % self.user.id
            return '<a href="%s" class="player">%s</a>' % (url, self.user.username)
        except:
            return '(None)'

    def state_text(self):
        try:
            return Order.STATES[self.state]
        except KeyError:
            return str(self.state)

    def __unicode__(self):
        return u'%s [%s]' % (self.date, self.state_text())


#------------------------------------------------------------------------------
class OrderRow(models.Model):

    class Meta:
        app_label = 'industry'
        ordering = ['order']

    order = models.ForeignKey(Order, related_name='rows')
    catalog_entry = models.ForeignKey(CatalogEntry, related_name='order_rows')
    quantity = models.PositiveIntegerField()
    cost = models.FloatField(default=0.0)
    surcharge = models.FloatField(default=0.0)

    def get_aggregated_jobs(self, activity=None):
        """
        Retrieve a list of all the jobs related to this OrderRow aggregated by item_id.

        The job activity can be filtered to display only SUPPLY jobs
        """
        where = [ '"row_id" = %s' ]
        if activity is not None:
            where.append('"activity" = %d' % activity)
        sql = 'SELECT "item_id", SUM("runs"), "activity" FROM "industry_job"'
        sql += ' WHERE ' + ' AND '.join(where)
        sql += ' GROUP BY "item_id", "activity" ORDER BY "activity", "item_id";'
        sql = db.fix_mysql_quotes(sql)

        cursor = connection.cursor() #@UndefinedVariable
        cursor.execute(sql, [self.id])

        jobs = []
        for i, r, a in cursor:
            jobs.append(Job(item_id=i, runs=r, activity=a))
        cursor.close()

        return jobs


    def create_jobs(self, prices=None):
        try:
            job = Job.create(self.catalog_entry_id, self.quantity, order=self.order, row=self)
            job.create_requirements()
        except InventionError, err:
            raise OrderCannotBeFulfilled(msg=unicode(err))
        cost, missing_prices = self.calculate_cost(prices)
        return cost, missing_prices


    def calculate_cost(self, prices=None):
        if prices is None:
            prices = {}
            for sp in Supply.objects.all():
                prices[sp.typeID] = sp.price
        cost = 0.0
        missing_prices = set([])
        for job in self.get_aggregated_jobs(Job.SUPPLY):
            try:
                job_price = prices[job.item_id] * round(job.runs)
                cost += job_price
            except KeyError:
                missing_prices.add(job.item_id)
        return cost, missing_prices

    def __unicode__(self):
        return '%s x%d' % (self.catalog_entry.typeName, self.quantity)



#------------------------------------------------------------------------------
class OrderCannotBeFulfilled(UserWarning):

    def __init__(self, msg=None, missing_blueprints=None, missing_prices=None):
        self.msg = msg
        self.missing_blueprints = missing_blueprints or []
        self.missing_prices = missing_prices or []

    def __unicode__(self):
        if self.msg:
            return self.msg
        if self.missing_blueprints:
            if all([ type(p) == type(0) for p in self.missing_blueprints ]):
                self.missing_blueprints = Type.objects.filter(typeID__in=self.missing_blueprints)\
                                                      .values_list('typeName', flat=True)
            output = u'Missing Blueprints: '
            output += u', '.join(map(str, self.missing_blueprints))
        elif self.missing_prices:
            if all([ type(p) == type(0) for p in self.missing_prices ]):
                self.missing_prices = Type.objects.filter(typeID__in=self.missing_prices)\
                                                  .values_list('typeName', flat=True)
            output = u'Missing Supply prices: '
            output += u', '.join(map(str, self.missing_prices))
        return output or u'nothing missing'

#------------------------------------------------------------------------------
class IllegalTransition(UserWarning): pass

