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


from django.contrib import admin
from ecm.apps.scheduler.models import ScheduledTask, GarbageCollector

class ScheduledTaskOptions(admin.ModelAdmin):
    list_display = ["function",
                    "frequency_admin_display",
                    "is_active",
                    "is_running",
                    "is_one_shot",
                    "is_last_exec_success",
                    "next_execution_admin_display",
                    "priority",
                    "launch_task_admin_display"]
    list_filter = ["is_active"]
    search_fields = ["function"]

class GarbageCollectorOptions(admin.ModelAdmin):
    list_display = ["model_admin_display",
                    "max_age_threshold_admin_display",
                    "min_entries_threshold"]

admin.site.register(ScheduledTask, ScheduledTaskOptions)
admin.site.register(GarbageCollector, GarbageCollectorOptions)
