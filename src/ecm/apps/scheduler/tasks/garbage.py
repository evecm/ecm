# Copyright (c) 2010-2011 Robin Jarry
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

__date__ = "2011-03-14"
__author__ = "diabeteman"


import logging

from django.db import transaction

from ecm.apps.scheduler.models import GarbageCollector

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def collect_garbage():
    try:
        count = 0
        for collector in GarbageCollector.objects.all():
            LOG.info("collecting old records for model: %s" % collector.db_table)
            model = collector.get_model()
            count = model.objects.all().count()

            if count > collector.min_entries_threshold:
                entries = model.objects.filter(date__lt=collector.get_expiration_date())
                for entry in entries:
                    entry.delete()

                deleted_entries = entries.count()
            else:
                deleted_entries = 0

            LOG.info("%d entries will be deleted" % deleted_entries)
            count += deleted_entries

        LOG.info("%d old records deleted" % count)
    except:
        # error catched, rollback changes
        LOG.exception("cleanup failed")
        raise

