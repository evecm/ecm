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

from optparse import make_option

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
    )
    def handle(self, *args, **options):

        all_tasks = ScheduledTask.objects.filter(is_active=True).order_by('function')
        all_tasks_txt = "\n  ".join([ t.function for t in all_tasks ])

        if options.get('all'):
            for task in all_tasks.order_by('-priority'):
                if options.get('reset'):
                    task.is_running = False
                if task.is_running:
                    raise CommandError('ScheduledTask "%s" is already running.' % task.function)
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
                if task.is_running:
                    raise CommandError('ScheduledTask "%s" is already running.' % task.function)
    
                task.run()
                self.stdout.write('Successfully executed "%s"\n' % task.function)
