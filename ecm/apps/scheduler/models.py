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

__date__ = "2011-03-09"
__author__ = "diabeteman"


import logging
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as tr
from django.utils.encoding import force_unicode
from django.utils import timezone
from django.db import models

from ecm.apps.scheduler.validators import (FunctionValidator, extract_function, extract_model,
                                           ModelValidator, extract_args, ArgsValidator)

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class ScheduledTask(models.Model):

    FREQUENCY_UNIT_CHOICES = (
        (1, tr("seconds")),
        (60, tr("minutes")),
        (3600, tr("hours")),
        (3600 * 24, tr("days")),
        (3600 * 24 * 7, tr("weeks"))
    )

    function = models.CharField(max_length=256, validators=[FunctionValidator()])
    args = models.CharField(max_length=256, default="{}", validators=[ArgsValidator()])
    priority = models.IntegerField(default=0)
    next_execution = models.DateTimeField(auto_now_add=True)
    last_execution = models.DateTimeField(null=True, blank=True)
    frequency = models.IntegerField()
    frequency_units = models.IntegerField(default=3600, choices=FREQUENCY_UNIT_CHOICES)
    is_active = models.BooleanField(default=True)
    is_scheduled = models.BooleanField(default=False)
    is_running = models.BooleanField(default=False)
    is_one_shot = models.BooleanField(default=False)
    is_last_exec_success = models.BooleanField(default=False)

    class Meta:
        verbose_name = tr("scheduled task")
        verbose_name_plural = tr("scheduled tasks")

    def __unicode__(self):
        return force_unicode(self.function)

    def frequency_admin_display(self):
        freq = self.frequency
        frequnits = self.get_frequency_units_display()
        return tr("Every " + str(freq) + " " + str(frequnits))
    frequency_admin_display.short_description = tr("frequency")

    def function_admin_display(self):
        return self.get_function_display()
    function_admin_display.short_description = tr("Function")

    def permalink(self, next_page=None):
        url = "/scheduler/tasks/%d/launch/" % self.id
        if next_page: url += "?next=%s" % next_page
        return url

    def as_html(self, next_page=None):
        return '<a class="task" href="%s">"%s"</a>' % (self.permalink(next_page), tr('Launch'))

    def launch_task_admin_display(self):
        return self.as_html(next_page="/admin/scheduler/scheduledtask/")
    launch_task_admin_display.allow_tags = True
    launch_task_admin_display.short_description = tr("Launch")

    def next_execution_admin_display(self):
        from ecm.utils.format import print_delta
        delta = self.next_execution - timezone.now()
        if delta < timedelta(0):
            delta = timedelta(0)
        return print_delta(delta)
    next_execution_admin_display.short_description = tr("Next execution")

    def get_function(self):
        return extract_function(self.function)

    def get_args(self):
        return extract_args(self.args)

    def run(self):
        try:
            if self.is_running:
                return
            else:
                self.is_running = True
                self.last_execution = timezone.now()
                self.save()

            invalid_function = False
            try:
                func = self.get_function()
            except ValidationError:
                invalid_function = True
                raise
            args = self.get_args()
            func(**args)

            self.is_last_exec_success = True
            # TODO : add listeners handling here
        except:
            # error during the execution of the task
            self.is_last_exec_success = False
            LOG.exception("")
        finally:
            if invalid_function:
                LOG.warning('Task "%s" is obsolete, deleting...' % self.function)
                self.delete()
            else:
                delta = self.frequency * self.frequency_units
                self.next_execution = timezone.now() + timedelta(seconds=delta)
                self.is_running = False
                self.is_scheduled = False
                self.save()

#------------------------------------------------------------------------------
class GarbageCollector(models.Model):

    AGE_UNIT_CHOICES = (
        (3600 * 24, tr("days")),
        (3600 * 24 * 7, tr("weeks")),
        (3600 * 24 * 7 * 30, tr("months"))
    )

    DATE_FIELD = 'DATE_FIELD'

    model = models.CharField(max_length=255, primary_key=True,
                             validators=[ModelValidator()])
    min_entries_threshold = models.BigIntegerField(default=10000)
    max_age_threshold = models.BigIntegerField()
    age_units = models.BigIntegerField(default=3600 * 24 * 7 * 30, choices=AGE_UNIT_CHOICES)

    def model_admin_display(self):
        return self.model
    model_admin_display.short_description = tr("Database Model")

    def max_age_threshold_admin_display(self):
        max_age_thres = self.max_age_threshold
        age_unit_disp = self.get_age_units_display()
        return '%s %s' % (max_age_thres, age_unit_disp)
    max_age_threshold_admin_display.short_description = tr("Max Age Threshold")

    def get_expiration_date(self):
        return timezone.now() + timedelta(seconds=self.max_age_threshold * self.age_units)

    def get_model(self):
        return extract_model(self.model)

    def model_has_date_field(self):
        model = self.get_model()
        if hasattr(model, self.DATE_FIELD):
            date_field_name = getattr(model, self.DATE_FIELD)
            for field in model._meta.fields:
                if field.name == date_field_name:
                    return True
        return False



