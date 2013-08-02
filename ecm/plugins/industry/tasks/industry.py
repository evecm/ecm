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

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

from ecm.utils.format import print_float
from ecm.apps.eve.models import Type
from ecm.plugins.industry.models.order import OrderCannotBeFulfilled
from ecm.plugins.industry.tasks import evecentral
#from ecm.plugins.industry.tasks import evemarketeer
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
        #buyPrices = evemarketeer.get_buy_prices(item_ids, supply_source.location_id)

        for supPrice in prices:
            try:
                if buyPrices[supPrice.typeID] > 0.0 and supPrice.price != buyPrices[supPrice.typeID]:
                    supPrice.update_price(buyPrices[supPrice.typeID])
                    logger.info('New price for "%s" -> %s' % (supPrice.item_admin_display(),
                                                          print_float(buyPrices[supPrice.typeID])))
            except KeyError:
                logger.info('Could not find buy-price for item: %d - skipping' % (supPrice.typeID))



#------------------------------------------------------------------------------
def update_all_production_costs():
    user = User.objects.latest('id')
    for entry in CatalogEntry.objects.filter(is_available=True):
        try:
            update_production_cost(entry, user)
        except Type.NoBlueprintException:
            # this can happen when blueprint requirements are not found in EVE database.
            # no way to work arround this issue for the moment, we just keep the price to None
            pass
        except OrderCannotBeFulfilled, err:
            if err.missing_prices:
                for supply in err.missing_prices:
                    Supply.objects.get_or_create(pk=supply)
            logger.warning('Cannot calculate production cost for "%s": %s', entry.typeName, err)

#------------------------------------------------------------------------------
def update_production_cost(entry, user):
    cost = None
    missing_bps = entry.missing_blueprints()
    if not missing_bps:
        with transaction.commit_manually():
            try:
                order = Order.objects.create(originator=user)
                order.modify( [ (entry, 1) ] )
                missing_prices = order.create_jobs(ignore_fixed_prices=True)
                if missing_prices:
                    raise OrderCannotBeFulfilled(missing_prices=missing_prices)
                else:
                    cost = order.quote
            finally:
                transaction.rollback()
    else:
        raise OrderCannotBeFulfilled(missing_blueprints=list(missing_bps))
    entry.production_cost = cost
    entry.last_update = timezone.now()
    entry.save()



