'''
This file is part of ESM

Created on 9 mars 2011
@author: diabeteman
'''

from django.contrib import admin
from ism.data.scheduler.models import ScheduledTask, GarbageCollector

class ScheduledTaskOptions(admin.ModelAdmin):
    list_display = ["function_admin_display", 
                    "frequency_admin_display", 
                    "is_active", 
                    "is_running", 
                    "next_execution_admin_display", 
                    "priority",
                    "launch_task_admin_display"]
    list_filter = ["is_active"]

class GarbageCollectorOptions(admin.ModelAdmin):
    list_display = ["db_table_admin_display", 
                    "max_age_threshold_admin_display", 
                    "min_entries_threshold"]

admin.site.register(ScheduledTask, ScheduledTaskOptions)
admin.site.register(GarbageCollector, GarbageCollectorOptions)