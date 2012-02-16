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
from ecm.plugins.industry.models.order import OrderCannotBeFulfilled

__date__ = "2011 8 20"
__author__ = "diabeteman"

import logging
from datetime import datetime

from django.db import transaction
from django.db.models.aggregates import Count

from ecm.core.eve.classes import NoBlueprintException
from ecm.core import utils
from ecm.plugins.industry.tasks import evecentral
from ecm.plugins.industry.models import Supply, SupplySource, Order, CatalogEntry

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
@transaction.commit_on_success
def update_supply_prices():
    supplyPrices = Supply.objects.filter(auto_update=True)
    for supply_source in SupplySource.objects.all():
        logger.debug('Updating supply prices for %s (%d)...' % (supply_source.name,supply_source.location_id))
        prices = supplyPrices.filter(supply_source=supply_source)
        item_ids = prices.values_list('typeID', flat=True)
        buyPrices = evecentral.get_buy_prices(item_ids, supply_source.location_id)

        for supPrice in prices:
            try:
                if buyPrices[supPrice.typeID] > 0.0 and supPrice.price != buyPrices[supPrice.typeID]:
                    supPrice.update_price(buyPrices[supPrice.typeID])
                    logger.info('New price for "%s" -> %s' % (supPrice.item_admin_display(),
                                                          utils.print_float(buyPrices[supPrice.typeID])))
            except KeyError:
                logger.info('Could not find buy-price for item: %d - skipping' % (supPrice.typeID))



#------------------------------------------------------------------------------
def update_production_costs():
    now = datetime.now()
    query = CatalogEntry.objects.all().annotate(bp_count=Count('blueprints'))
    for entry in query.filter(bp_count__gt=0):
        cost = None
        try:
            missing_bps = entry.missing_blueprints()
            if not missing_bps:
                with transaction.commit_manually():
                    try:
                        order = Order.objects.create(originator_id=1)
                        order.modify( [ (entry, 1) ] )
                        missingPrices = order.create_jobs()
                        if not missingPrices:
                            cost = order.cost
                    finally:
                        transaction.rollback()
            else:
                raise OrderCannotBeFulfilled(missing_blueprints=list(missing_bps))
        except NoBlueprintException:
            # this can happen when blueprint requirements are not found in EVE database.
            # no way to work arround this issue for the moment, we just keep the price to None
            pass
        except OrderCannotBeFulfilled, err:
            logger.warning('Cannot calculate production cost for "%s": %s', entry.typeName, err)
        entry.production_cost = cost
        entry.last_update = now
        entry.save()
