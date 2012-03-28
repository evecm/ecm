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

__date__ = "2011-03-09"
__author__ = "diabeteman"

import logging
from threading import Thread, RLock
import Queue

from django.conf import settings

#------------------------------------------------------------------------------
class Scheduler(object):

    _INSTANCE = None

    @staticmethod
    def instance():
        """
        Singleton design pattern.
        """
        if Scheduler._INSTANCE is None:
            Scheduler._INSTANCE = Scheduler(settings.SCHEDULER_MAX_CONCURRENT_TASKS)
        return Scheduler._INSTANCE

    def __init__(self, max_concurrent_tasks=1):
        self._max_concurrent_tasks = max_concurrent_tasks
        self._queue = Queue.Queue()
        self._workers = 0
        self._workers_lock = RLock()
        self.log = logging.getLogger(__name__)
        self.log.debug('Scheduler instance %r created', id(self))

    def schedule(self, *tasks):
        """
        Appends new tasks to the task queue. Starts new workers if needed.
        """
        for task in tasks:
            self._queue.put(task, timeout=2)
        if tasks:
            self.log.debug('Scheduling %r tasks', len(tasks))
        with self._workers_lock:
            while self._workers < self._max_concurrent_tasks:
                worker = Scheduler.Worker()
                worker.start()
                self._workers += 1
            self.log.debug('%r workers running', self._workers)


    def _remove_one_worker(self):
        """
        Count one worker as dead.
        This method is to be called by workers themselves before they die.
        """
        with self._workers_lock:
            if self._workers > 0:
                self._workers -= 1
            self.log.debug('%r workers running', self._workers)

    #--------------------------------------------------
    class Worker(Thread):
        """
        Worker thread that executes tasks.
        """
        #override
        def run(self):
            """
            Gets tasks from the Scheduler and executes them one at a time.
            When the Scheduler task_queue is empty, notify the scheduler that we're done.
            """
            log = logging.getLogger(__name__)
            log.debug('Worker %r started', id(self))
            more_tasks = True
            while more_tasks:
                try:
                    task = Scheduler.instance()._queue.get(timeout=2)
                    log.debug('Task "%s" started', str(task))
                    task.run()
                    log.debug('Task "%s" done', str(task))
                    Scheduler.instance()._queue.task_done()
                except Queue.Empty:
                    log.debug('Worker %r: no more tasks to execute', id(self))
                    more_tasks = False
            log.debug('Worker %r dying', id(self))
            Scheduler.instance()._remove_one_worker()


