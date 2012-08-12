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

__date__ = "2012 1 26"
__author__ = "diabeteman"

import os
import logging
import itertools
from optparse import make_option

from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError

from ecm.apps.scheduler.models import ScheduledTask

#------------------------------------------------------------------------------
class Command(BaseCommand):
    args = '<task_name task_name ...>'
    help = 'Executes the specified tasks' #@ReservedAssignment
    option_list = BaseCommand.option_list + (
        make_option('--reset',
            action='store_true',
            dest='reset',
            default=False,
            help='Force reset "running" tasks before execution.'),
        make_option('--all',
            action='store_true',
            dest='all',
            default=False,
            help='Run all tasks ordered by decreasing priority.'),
        make_option('--cron',
            action='store_true',
            dest='cron',
            default=False,
            help='Run tasks that need running ordered by decreasing priority.'),
        make_option('--silent',
            action='store_true',
            dest='silent',
            default=False,
            help='Disable console output.'),
    )
    def handle(self, *args, **options):

        all_tasks = ScheduledTask.objects.filter(is_active=True).order_by('function')
        all_tasks_txt = "\n  ".join([ t.function for t in all_tasks ])

        if options.get('silent'):
            self.stdout = file(os.devnull, 'a')
            # disable console loggers
            logger = logging.getLogger('ecm')
            is_console = lambda h: h.__class__ == logging.StreamHandler
            # modify the list in-place so that any references to it will be updated as well
            logger.handlers[:] = list(itertools.ifilterfalse(is_console, logger.handlers))

        if options.get('all'):
            for task in all_tasks.order_by('-priority'):
                if options.get('reset'):
                    task.is_running = False
                    task.is_scheduled = False
                if task.is_running:
                    raise CommandError('ScheduledTask "%s" is already running.' % task.function)
                task.run()
        elif options.get('cron'):
            now = timezone.now()
            query = ScheduledTask.objects.filter(is_active=True,
                                                 is_running=False,
                                                 is_scheduled=False,
                                                 next_execution__lt=now)
            tasks_to_execute = list(query.order_by("-priority"))
            self.stdout.write('[ECM] %d tasks to execute.\n' % query.count())
            query.update(is_scheduled=True)
            for task in tasks_to_execute:
                task.run()
        elif len(args) == 0:
            raise CommandError('No ScheduledTask name provided. \n\n' +
                               'Please choose one of: \n  %s\n' % all_tasks_txt)
        else:
            for task_name in args:
                tasks = all_tasks.filter(function__contains=task_name)
    
                if len(tasks) > 1:
                    tasks_txt = "\n  ".join([ t.function for t in tasks ])
                    raise CommandError('Multiple ScheduledTasks found with "%s" in their name. \n  %s\n'
                                       % (task_name, tasks_txt))
                elif len(tasks) == 0:
                    raise CommandError('No ScheduledTask found with "%s" in their name. \n\n'
                                       'Please choose one of: \n  %s\n' % (task_name, all_tasks_txt))
                task = tasks[0]
                if options.get('reset'):
                    task.is_running = False
                    task.is_scheduled = False
                if task.is_running:
                    raise CommandError('ScheduledTask "%s" is already running.' % task.function)
    
                task.run()
                
                if task.is_last_exec_success:
                    self.stdout.write('Successfully executed "%s"\n' % task.function)
                else:
                    self.stdout.write('ERROR in task "%s"\n' % task.function)
