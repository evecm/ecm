'''
This file is part of ESM

Created on 9 mars 2011
@author: diabeteman
'''
from threading import Thread
from datetime import datetime, timedelta

import logging.config
from ism import settings



logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("scheduler")



class TaskThread(Thread):
    
    def __init__(self, tasks):
        super(self.__class__,self).__init__()
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
                logger.info(task.function + " triggered")
                task.get_function()()
                logger.info(task.function + " done")
            finally:
                delta = task.frequency * task.frequency_units
                task.next_execution = datetime.now() + timedelta(seconds=delta)
                task.is_running = False
                task.save()