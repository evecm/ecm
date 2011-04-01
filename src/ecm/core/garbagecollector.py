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

__date__ = "2011-03-14"
__author__ = "diabeteman"



from django.db import transaction


import logging
from ecm.data.scheduler.models import GarbageCollector

logger = logging.getLogger(__name__)


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
