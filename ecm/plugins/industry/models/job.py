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

__date__ = "2015 1 21"
__author__ = "diabeteman"

from django.db import models
from django.contrib.auth.models import User

from ecm.utils.tools import cached_property
from ecm.apps.eve.models import Type
from ecm.plugins.industry.models.research import InventionPolicy
from ecm.plugins.industry.models.catalog import OwnedBlueprint

#------------------------------------------------------------------------------
class Job(models.Model):

    class Meta:
        app_label = 'industry'

    PENDING = 0
    PLANNED = 1
    IN_PRODUCTION = 2
    READY = 3

    STATES = {
        PENDING:       'Pending',
        PLANNED:       'Planned',
        IN_PRODUCTION: 'In Production',
        READY:         'Ready',
    }

    SUPPLY = 0
    MANUFACTURING = 1
    INVENTION = 8

    ACTIVITIES = {
        MANUFACTURING: 'Manufacturing',
        SUPPLY:        'Supply',
        INVENTION:     'Invention',
    }

    # self.order is None if this is an aggregation job
    order = models.ForeignKey('Order', related_name='jobs', null=True, blank=True)
    # self.row is not None only if this is a root job
    row = models.ForeignKey('OrderRow', related_name='jobs', null=True, blank=True)
    # self.parent_job is None if this job is directly issued from an OrderRow
    parent_job = models.ForeignKey('self', related_name='children_jobs', null=True, blank=True)

    state = models.SmallIntegerField(default=PENDING, choices=STATES.items())

    assignee = models.ForeignKey(User, related_name='jobs', null=True, blank=True)

    item_id = models.PositiveIntegerField()
    # runs must be a float number, else when jobs are aggregated there may be rounding errors
    runs = models.FloatField()
    blueprint = models.ForeignKey('OwnedBlueprint', related_name='jobs',
                                  null=True, blank=True,
                                  on_delete=models.SET_NULL)
    activity = models.SmallIntegerField(default=MANUFACTURING, choices=ACTIVITIES.items())

    due_date = models.DateField(null=True, blank=True)
    duration = models.BigIntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def create_requirements(self):
        """
        Recursively create all jobs needed to complete the current one.

        SUPPLY jobs are trivial, they stop the recursion.
        """
        if self.activity == Job.SUPPLY:
            return # stop recursion

        materials = self.blueprint.get_bill_of_materials(activity=self.activity,
                                                         runs=self.runs,
                                                         me_level=self.blueprint.me)

        for mat in materials:
            self.children_jobs.add(Job.create(item_id=mat.requiredTypeID,
                                              quantity=mat.quantity,
                                              order=self.order,
                                              row=self.row))

        parent_bp_id = self.blueprint.parentBlueprintTypeID
        if parent_bp_id is not None and self.blueprint.invented:
            # only create invention jobs if we don't own a BPO/BPC
            attempts  = InventionPolicy.attempts(self.blueprint)

            # Since invented blueprints have fixed number of runs, we need to
            # prorate the number of invention jobs that will be actually charged
            # to the client.
            effective_runs = self.runs / float(self.blueprint.runs) * attempts

            # create a temp OwnedBlueprint that will be used to run the invention
            bpc = OwnedBlueprint.objects.create(typeID=parent_bp_id, copy=True)
            # add an INVENTION job
            self.children_jobs.create(item_id=parent_bp_id,
                                      blueprint=bpc,
                                      runs=effective_runs,
                                      order=self.order,
                                      row=self.row,
                                      activity=Job.INVENTION)

        if self.activity == Job.INVENTION:
            # add a SUPPLY job for T1 BPCs
            self.children_jobs.create(item_id=self.blueprint.typeID,
                                      runs=round(self.runs),
                                      order=self.order,
                                      row=self.row,
                                      activity=Job.SUPPLY)
            decriptorTypeID  = InventionPolicy.decryptor(self.parent_job.blueprint)
            if decriptorTypeID is not None:
                # add a SUPPLY job for a decryptor if needed
                self.children_jobs.create(item_id=decriptorTypeID,
                                          runs=round(self.runs),
                                          order=self.order,
                                          row=self.row,
                                          activity=Job.SUPPLY)

        for job in self.children_jobs.all():
            # recursive call
            job.create_requirements()



    @staticmethod
    def create(item_id, quantity, order, row):
        """
        Create a job (MANUFACTURING by default).

        If the item cannot be manufactured or if the corp does not own
        the blueprint needed for the item, a SUPPLY job is created.

        The number of runs is calculated from the needed quantity
        """
        item = Type.objects.select_related(depth=2).get(pk=item_id)
        try:
            if item.blueprint is None:
                # item cannot be manufactured
                bp = None
                activity = Job.SUPPLY
                duration = 0
                runs = quantity
            else:
                bpid = item.blueprintTypeID
                activity = Job.MANUFACTURING
                bp = OwnedBlueprint.objects.filter(typeID=bpid, copy=False).order_by('-me')[0]
                runs = quantity / item.portionSize
                if quantity % item.portionSize:
                    runs += 1
                duration = bp.manufacturing_time(runs)
        except IndexError:
            if item.metaGroupID == 2 and item.blueprint.parent_blueprint is not None:
                # we're trying to manufacture a T2 item without owning its BPO
                # we must create an OwnedBlueprint for this job only (that will
                # be consumed with it)
                # The invention policies are to be specified in InventionPolicies
                activity = Job.MANUFACTURING
                bp = InventionPolicy.blueprint(item.blueprint)
                runs = quantity / item.portionSize
                if quantity % item.portionSize:
                    runs += 1
                duration = bp.manufacturing_time(runs)
                bp.save()
            else:
                bp = None
                activity = Job.SUPPLY
                duration = 0
                runs = quantity

        return Job.objects.create(order=order,
                                  row=row,
                                  item_id=item_id,
                                  blueprint=bp,
                                  runs=runs,
                                  activity=activity,
                                  duration=duration)

    def repr_as_tree(self, indent=0):
        output = '    ' * indent + '-> ' + unicode(self) + '\n'
        for j in self.children_jobs.all():
            output += j.repr_as_tree(indent + 1)
        return output

    def url(self):
        return '/industry/jobs/%d/' % self.id

    def permalink(self):
        return '<a href="%s" class="industry-job">Job &#35;%s</a>' % (self.url(), self.id)

    def assignee_permalink(self):
        if self.assignee is not None:
            url = '/hr/players/%d/' % self.assignee.id
            return '<a href="%s" class="player">%s</a>' % (url, self.assignee.username)
        else:
            return '(none)'

    @cached_property
    def item(self):
        return Type.objects.get(pk=self.item_id)

    @property
    def state_text(self):
        return Job.STATES[self.state]

    @property
    def activity_text(self):
        return Job.ACTIVITIES[self.activity]

    def __unicode__(self):
        return u"[%s] %s x%d" % (self.activity_text, self.item.typeName, int(round(self.runs)))
