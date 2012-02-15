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

__date__ = "2011 8 20"
__author__ = "diabeteman"

import logging
from datetime import datetime

from django.db import transaction

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
    for entry in CatalogEntry.objects.all():
        cost = None
        try:
            if not entry.missing_blueprints():
                order = Order.objects.create(originator_id=1)
                order.modify( [ (entry, 1) ] )
                missingPrices = order.create_jobs()
                if not missingPrices:
                    cost = order.cost
        except NoBlueprintException:
            # this can happen when blueprint requirements are not found in EVE database.
            # no way to work arround this issue for the moment, we just keep the price to None
            pass
        entry.production_cost = cost
        entry.last_update = now
        entry.save()
