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

__date__ = "2011 8 19"
__author__ = "diabeteman"

import logging
import time

from django.db import connections, transaction
from django.shortcuts import render_to_response
from django.template.context import RequestContext as Ctx

from ecm.core import utils
from ecm.apps.eve.models import Type, BlueprintReq
from ecm.apps.eve import constants
from ecm.plugins.industry.models import CatalogEntry, Supply

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
def home(request):
    return render_to_response('industry_home.html', {}, Ctx(request))


#------------------------------------------------------------------------------
@transaction.commit_on_success
def create_missing_catalog_entries():
    start = time.time()
    manufacturable_types = Type.objects.filter(blueprint__isnull=False,
                                               published=1,
                                               metaGroupID__in=constants.MANUFACTURABLE_ITEMS,
                                               market_group__isnull=False)
    manufacturable_types = manufacturable_types.exclude(typeID__in=constants.FACTION_FRIGATES_TYPEIDS)
    eve_typeIDs = set(manufacturable_types.values_list('typeID', flat=True))
    ecm_typeIDs = set(CatalogEntry.objects.values_list('typeID', flat=True))

    missing_ids = list(eve_typeIDs - ecm_typeIDs)

    for sublist in utils.sublists(missing_ids, 50):
        for obj in Type.objects.filter(typeID__in=sublist):
            CatalogEntry.objects.create(typeID=obj.typeID, typeName=obj.typeName, is_available=False)

    if missing_ids:
        duration = time.time() - start
        logger.info('added %d missing catalog entries (took %.2f sec.)', len(missing_ids), duration)
create_missing_catalog_entries()

#------------------------------------------------------------------------------
@transaction.commit_on_success
def create_missing_supplies():
    start = time.time()
    eve_supplies = BlueprintReq.objects.filter(required_type__blueprint__isnull=True,
                                               required_type__published=1,
                                               damagePerJob__gt=0.0)
    eve_typeIDs = set(eve_supplies.values_list('required_type', flat=True).distinct())
    ecm_typeIDs = set(Supply.objects.values_list('typeID', flat=True))

    missing_ids = eve_typeIDs - ecm_typeIDs

    for typeID in missing_ids:
        Supply.objects.create(typeID=typeID)

    if missing_ids:
        duration = time.time() - start
        logger.info('added %d missing supplies (took %.2f sec.)', len(missing_ids), duration)
create_missing_supplies()
