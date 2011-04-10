# The MIT License - EVE Corporation Management
# 
# Copyright (c) 2010 Robin Jarry
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__date__ = "2011-03-09"
__author__ = "diabeteman"




from threading import Thread
from datetime import datetime, timedelta

import logging
logger = logging.getLogger(__name__)



class TaskThread(Thread):
    
    def __init__(self, tasks):
        super(self.__class__, self).__init__()
        self.tasks = tasks
        
    def run(self):
        logger.debug("executing %d task(s)" % len(self.tasks))
        for task in self.tasks:
            try:
                if task.is_running:
                    continue
                else:
                    task.is_running = True
                    task.save()
                logger.info(unicode(task) + " triggered")
                task.run()
                logger.info(unicode(task) + " done")
            finally:
                if task.one_shot:
                    task.delete()
                else:
                    delta = task.frequency * task.frequency_units
                    task.next_execution = datetime.now() + timedelta(seconds=delta)
                    task.is_running = False
                    task.save()
