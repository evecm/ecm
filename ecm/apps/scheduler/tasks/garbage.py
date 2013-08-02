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

__date__ = "2011-03-14"
__author__ = "diabeteman"


import logging

from django.db import transaction

from ecm.apps.scheduler.models import GarbageCollector

LOG = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def collect_garbage():
    for collector in GarbageCollector.objects.all():
        collect_one(collector)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def collect_one(collector):
    LOG.info("collecting old records for model: %s" % collector.model)
    model = collector.get_model()

    if collector.model_has_date_field() and model.objects.all().count() > collector.min_entries_threshold:
        filter_args = { model.DATE_FIELD + '__lt': collector.get_expiration_date() }
        entries = model.objects.filter(**filter_args)
        deleted_entries = entries.count()
        entries.delete()
    else:
        deleted_entries = 0

    LOG.info("%d entries deleted" % deleted_entries)
