'''
This file is part of ESM

Created on 9 march 2011
@author: diabeteman
'''

from datetime import datetime, timedelta
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.db import models
from esm.data.scheduler.validators import FunctionValidator, extract_function
import sys



class ScheduledTask(models.Model):
    
    FREQUENCY_UNIT_CHOICES = (
        (1, _("seconds")),
        (60, _("minutes")),
        (3600, _("hours")),
        (3600 * 24, _("days")),
        (3600 * 24 * 7, _("weeks"))
    )
    
    FUNCTION_CHOICES = (
        ("esm.core.parsers.corp.update",        "Update corp details"),
        ("esm.core.parsers.assets.update",      "Update assets"),
        ("esm.core.parsers.membertrack.update", "Update members"),
        ("esm.core.parsers.membersecu.update",  "Update security accesses"),
        ("esm.core.parsers.outposts.update",    "Update ouposts"),
        ("esm.core.parsers.titles.update",      "Update titles"),
        ("esm.core.garbagecollector.run",       "Delete old records for the database")
    )
    
    function = models.CharField(max_length=255, primary_key=True,
                                validators=[FunctionValidator()],
                                choices=FUNCTION_CHOICES)
    next_execution = models.DateTimeField(default=datetime.now())
    frequency = models.IntegerField()
    frequency_units = models.IntegerField(default=3600, choices=FREQUENCY_UNIT_CHOICES)
    is_active = models.BooleanField(default=True)
    is_running = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = _("scheduled task")
        verbose_name_plural = _("scheduled tasks")
        ordering = ("-priority", "function")
    
    def get_function(self):
        return extract_function(self.function)
    
    def __unicode__(self):
        return force_unicode(self.function)
    
    def frequency_admin_display(self):
        return ugettext("Every %s %s") % (self.frequency, self.get_frequency_units_display())
    frequency_admin_display.short_description = "frequency"
    
    def function_admin_display(self):
        return self.get_function_display()
    function_admin_display.short_description = "Function"
    
    def get_url(self, next=None):
        url = "/tasks/launch/%s" % self.function
        if next: url += "?next=%s" % next
        return url
    
    def launch_task_admin_display(self):
        return '<a href="%s">Launch task</a>' % self.get_url(next="/admin/scheduler/scheduledtask/")
    launch_task_admin_display.allow_tags = True
    launch_task_admin_display.short_description = "Launch"
    
    def next_execution_admin_display(self):
        delta = self.next_execution - datetime.now()
        if delta < timedelta(0):
            delta = timedelta(0)
        hours, remainder = divmod(delta.seconds, 3600)
        minutes = divmod(remainder, 60)[0]
        return "%dh %dm" % (hours, minutes)
    next_execution_admin_display.short_description = "Next execution"



class GarbageCollector(models.Model):
    
    AGE_UNIT_CHOICES = (
        (3600 * 24, _("days")),
        (3600 * 24 * 7, _("weeks")),
        (3600 * 24 * 7 * 30, _("months"))
    )
    
    DB_TABLE_CHOICES = (
        ("esm.data.roles.models.RoleMemberDiff",    "Role membership history"),
        ("esm.data.roles.models.TitleMemberDiff",   "Title membership history"),
        ("esm.data.roles.models.MemberDiff",        "Member history"),
        ("esm.data.roles.models.TitleCompoDiff",    "Titles modifications history"),
        ("esm.data.assets.models.DbAssetDiff",      "Assets history")
    )
    
    db_table = models.CharField(max_length=255, primary_key=True,
                             choices=DB_TABLE_CHOICES)
    min_entries_threshold = models.PositiveIntegerField(default=10000)
    max_age_threshold = models.PositiveIntegerField()
    age_units = models.IntegerField(default=3600 * 24 * 7 * 30, choices=AGE_UNIT_CHOICES)
    
    def db_table_admin_display(self):
        return self.get_db_table_display()
    db_table_admin_display.short_description = "DB Table"
    
    def max_age_threshold_admin_display(self):
        return ugettext("%d %s") % (self.max_age_threshold, self.get_age_units_display())
    max_age_threshold_admin_display.short_description = "Max Age Threshold"
    
    def get_model(self):
        module, model = self.db_table.rsplit('.', 1)
        __import__(module)
        mod = sys.modules[module]
        return mod.__dict__[model]
    
    def get_expiration_date(self):
        return datetime.now() + timedelta(self.max_age_threshold * self.age_units)
    
    
    
    