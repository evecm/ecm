'''
This file is part of ESM

Created on 14 mars 2011
@author: diabeteman
'''
from django.db import transaction


import logging.config
from esm import settings
from esm.data.scheduler.models import GarbageCollector

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("garbage_collector")


@transaction.commit_manually
def run():
    try:
        count = 0
        for collector in GarbageCollector.objects.all():
            count += collect_garbage(collector)
        
        logger.debug("commiting modifications to database...")
        transaction.commit()
        logger.info("%d old records deleted" % count)
    except Exception, e:
        # error catched, rollback changes
        transaction.rollback()
        import sys, traceback
        errortrace = traceback.format_exception(type(e), e, sys.exc_traceback)
        logger.error("".join(errortrace))
        raise
    
    
    
def collect_garbage(collector):
    logger.debug("collecting old records for model: %s" % collector.db_table)
    model = collector.get_model()
    count = model.objects.all().count()
    
    if count > collector.min_entries_threshold:
        entries = model.objects.filter(date__lt=collector.get_expiration_date())
        for entry in entries:
            entry.delete()
        
        deleted_entries = entries.count()
    else:
        deleted_entries = 0
    
    logger.debug("%d entries will be deleted" % deleted_entries)    
    return deleted_entries
